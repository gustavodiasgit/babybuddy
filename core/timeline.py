# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from typing import Any, NotRequired, TypedDict

from django.urls import reverse
from django.utils import timezone, timesince
from django.utils.translation import gettext as _

from core.models import (
    DiaperChange,
    Feeding,
    Note,
    Sleep,
    TummyTime,
    Temperature,
    Medication,
)
from core.utils import duration_string


class TimelineEvent(TypedDict):
    """Estrutura compartilhada pelos eventos exibidos na timeline."""

    time: datetime
    details: list[str]
    edit_link: str
    model_name: str
    tags: Any
    event: NotRequired[str]
    type: NotRequired[str | None]
    duration: NotRequired[str]
    time_since_prev: NotRequired[str | None]


def _build_timeline_event(
    instance,
    event_time,
    message,
    details,
    edit_link,
    *,
    event_type=None,
    duration=None,
    time_since_prev=None,
    include_time_since_prev=False,
) -> TimelineEvent:
    """Cria um evento da timeline com os campos compartilhados."""

    event: TimelineEvent = {
        "time": timezone.localtime(event_time),
        "event": message,
        "details": details,
        "edit_link": edit_link,
        "model_name": instance.model_name,
        "tags": instance.tags.all(),
    }

    if event_type is not None:
        event["type"] = event_type

    if duration is not None:
        event["duration"] = duration

    if include_time_since_prev:
        event["time_since_prev"] = time_since_prev

    return event


def _get_duration(instance):
    """Formata a duração somente quando ela for maior que zero."""

    if instance.duration > timedelta(seconds=0):
        return duration_string(instance.duration)

    return None


def _get_feeding_instances(min_date, max_date, child=None):
    """Busca os feedings necessários para a timeline e para o cálculo anterior."""

    yesterday = min_date - timedelta(days=1)

    instances = Feeding.objects.filter(start__range=(yesterday, max_date)).order_by(
        "start"
    )

    if child:
        instances = instances.filter(child=child)

    return instances


def _get_feeding_details(instance):
    """Monta os detalhes exibidos para um feeding."""

    details = []

    if instance.notes:
        details.append(instance.notes)

    if instance.amount:
        details.append(_("Amount") + ": " + str(instance.amount))

    return details


def get_objects(date, child=None):
    """
    Create a time-sorted dictionary of all events for a child.
    :param date: a DateTime instance for the day to be summarized.
    :param child: Child instance to filter results for (no filter if `None`).
    :returns: a list of the day's events.
    """
    min_date = date
    max_date = date.replace(hour=23, minute=59, second=59)
    events = []

    _add_diaper_changes(min_date, max_date, events, child)
    _add_feedings(min_date, max_date, events, child)
    _add_medication(min_date, max_date, events, child)
    _add_sleeps(min_date, max_date, events, child)
    _add_tummy_times(min_date, max_date, events, child)
    _add_notes(min_date, max_date, events, child)
    _add_temperature_measurements(min_date, max_date, events, child)

    explicit_type_ordering = {"start": 0, "end": 1}
    events.sort(
        key=lambda x: (
            x["time"],
            explicit_type_ordering.get(x.get("type"), -1),
        ),
        reverse=True,
    )

    return events


def _add_tummy_times(min_date, max_date, events, child=None):
    instances = TummyTime.objects.filter(start__range=(min_date, max_date)).order_by(
        "-start"
    )

    if child:
        instances = instances.filter(child=child)

    for instance in instances:
        details = []

        if instance.milestone:
            details.append(instance.milestone)

        edit_link = reverse("core:tummytime-update", args=[instance.id])

        events.append(
            _build_timeline_event(
                instance=instance,
                event_time=instance.start,
                message=_("%(child)s started tummy time!")
                % {"child": instance.child.first_name},
                details=details,
                edit_link=edit_link,
                event_type="start",
            )
        )

        events.append(
            _build_timeline_event(
                instance=instance,
                event_time=instance.end,
                message=_("%(child)s finished tummy time.")
                % {"child": instance.child.first_name},
                details=details,
                edit_link=edit_link,
                event_type="end",
                duration=_get_duration(instance),
            )
        )


def _add_sleeps(min_date, max_date, events, child=None):
    instances = Sleep.objects.filter(start__range=(min_date, max_date)).order_by(
        "-start"
    )

    if child:
        instances = instances.filter(child=child)

    for instance in instances:
        details = []

        if instance.notes:
            details.append(instance.notes)

        edit_link = reverse("core:sleep-update", args=[instance.id])

        events.append(
            _build_timeline_event(
                instance=instance,
                event_time=instance.start,
                message=_("%(child)s fell asleep.")
                % {"child": instance.child.first_name},
                details=details,
                edit_link=edit_link,
                event_type="start",
            )
        )

        events.append(
            _build_timeline_event(
                instance=instance,
                event_time=instance.end,
                message=_("%(child)s woke up.") % {"child": instance.child.first_name},
                details=details,
                edit_link=edit_link,
                event_type="end",
                duration=_get_duration(instance),
            )
        )


def _add_feedings(min_date, max_date, events, child=None):
    instances = _get_feeding_instances(min_date, max_date, child)
    prev_start = None

    for instance in instances:
        time_since_prev = None

        if prev_start:
            time_since_prev = timesince.timesince(
                prev_start,
                now=instance.start,
            )

        prev_start = instance.start

        if instance.start < min_date:
            continue

        details = _get_feeding_details(instance)
        edit_link = reverse("core:feeding-update", args=[instance.id])

        if instance.duration > timedelta(seconds=0):
            events.append(
                _build_timeline_event(
                    instance=instance,
                    event_time=instance.start,
                    message=_("%(child)s started feeding.")
                    % {"child": instance.child.first_name},
                    details=details,
                    edit_link=edit_link,
                    event_type="start",
                    time_since_prev=time_since_prev,
                    include_time_since_prev=True,
                )
            )

            events.append(
                _build_timeline_event(
                    instance=instance,
                    event_time=instance.end,
                    message=_("%(child)s finished feeding.")
                    % {"child": instance.child.first_name},
                    details=details,
                    edit_link=edit_link,
                    event_type="end",
                    duration=duration_string(instance.duration),
                )
            )

        else:
            events.append(
                _build_timeline_event(
                    instance=instance,
                    event_time=instance.start,
                    message=_("%(child)s had a feeding.")
                    % {"child": instance.child.first_name},
                    details=details,
                    edit_link=edit_link,
                    time_since_prev=time_since_prev,
                    include_time_since_prev=True,
                )
            )


def _add_diaper_changes(min_date, max_date, events, child):
    instances = DiaperChange.objects.filter(time__range=(min_date, max_date)).order_by(
        "-time"
    )
    if child:
        instances = instances.filter(child=child)
    for instance in instances:
        contents = []
        if instance.wet:
            contents.append("💧")
        if instance.solid:
            contents.append("💩")
        events.append(
            {
                "time": timezone.localtime(instance.time),
                "event": _("%(child)s had a %(type)s diaper change.")
                % {
                    "child": instance.child.first_name,
                    "type": "".join(contents),
                },
                "edit_link": reverse("core:diaperchange-update", args=[instance.id]),
                "model_name": instance.model_name,
                "tags": instance.tags.all(),
            }
        )


def _add_medication(min_date, max_date, events, child):
    instances = Medication.objects.filter(time__range=(min_date, max_date)).order_by(
        "-time"
    )
    if child:
        instances = instances.filter(child=child)
    for instance in instances:
        details = []
        if instance.dosage:
            details.append(
                _("Dosage")
                + ": "
                + str(instance.dosage)
                + " "
                + instance.get_dosage_unit_display()
            )
        if instance.notes:
            details.append(instance.notes)
        edit_link = reverse("core:medication-update", args=[instance.id])

        events.append(
            {
                "time": timezone.localtime(instance.time),
                "event": _("%(child)s took %(medication)s.")
                % {
                    "child": instance.child.first_name,
                    "medication": instance.name,
                },
                "details": details,
                "edit_link": edit_link,
                "model_name": instance.model_name,
                "type": "start" if instance.next_dose_time else None,
                "tags": instance.tags.all(),
            }
        )
        if instance.next_dose_time:
            events.append(
                {
                    "time": timezone.localtime(instance.next_dose_time),
                    "event": _("%(child)s's %(medication)s dose wore off.")
                    % {
                        "child": instance.child.first_name,
                        "medication": instance.name,
                    },
                    "details": [],
                    "edit_link": edit_link,
                    "model_name": instance.model_name,
                    "type": "end",
                    "tags": instance.tags.all(),
                }
            )


def _add_notes(min_date, max_date, events, child):
    instances = Note.objects.filter(time__range=(min_date, max_date)).order_by("-time")
    if child:
        instances = instances.filter(child=child)
    for instance in instances:
        events.append(
            {
                "time": timezone.localtime(instance.time),
                "details": [instance.note],
                "edit_link": reverse("core:note-update", args=[instance.id]),
                "model_name": instance.model_name,
                "tags": instance.tags.all(),
            }
        )


def _add_temperature_measurements(min_date, max_date, events, child):
    instances = Temperature.objects.filter(time__range=(min_date, max_date)).order_by(
        "-time"
    )
    if child:
        instances = instances.filter(child=child)
    for instance in instances:
        details = []
        if instance.notes:
            details.append(instance.notes)
        if instance.temperature:
            details.append(_("Temperature") + ": " + str(instance.temperature))
        events.append(
            {
                "time": timezone.localtime(instance.time),
                "event": _("%(child)s had a temperature measurement.")
                % {
                    "child": instance.child.first_name,
                },
                "details": details,
                "edit_link": reverse("core:temperature-update", args=[instance.id]),
                "model_name": instance.model_name,
                "tags": instance.tags.all(),
            }
        )
