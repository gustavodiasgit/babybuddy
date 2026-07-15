# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from typing import Any, NotRequired, TypedDict

from django.urls import reverse
from django.utils import timezone, timesince
from django.utils.translation import gettext as _
from django.db.models import Q

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
    time: datetime
    event: str
    details: list
    edit_link: str
    model_name: str
    tags: Any
    type: NotRequired[str]
    duration: NotRequired[str]
    time_since_prev: NotRequired[str | None]


_UNSET = object()


def _build_timeline_event(
    instance,
    event_time,
    message,
    details,
    edit_link,
    *,
    event_type=None,
    duration=None,
    time_since_prev=_UNSET,
) -> TimelineEvent:
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

    if time_since_prev is not _UNSET:
        event["time_since_prev"] = time_since_prev

    return event


def _is_in_range(value, min_date, max_date):
    return min_date <= value <= max_date


def _duration_instances_for_day(model, min_date, max_date, child=None):
    instances = model.objects.filter(
        Q(start__range=(min_date, max_date)) | Q(end__range=(min_date, max_date))
    ).distinct()

    if child:
        instances = instances.filter(child=child)

    return instances.order_by("-start")


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
    instances = _duration_instances_for_day(
        TummyTime,
        min_date,
        max_date,
        child,
    )

    for instance in instances:
        details = []

        if instance.milestone:
            details.append(instance.milestone)

        edit_link = reverse("core:tummytime-update", args=[instance.id])

        if _is_in_range(instance.start, min_date, max_date):
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

        if _is_in_range(instance.end, min_date, max_date):
            duration = None

            if instance.duration > timedelta(seconds=0):
                duration = duration_string(instance.duration)

            events.append(
                _build_timeline_event(
                    instance=instance,
                    event_time=instance.end,
                    message=_("%(child)s finished tummy time.")
                    % {"child": instance.child.first_name},
                    details=details,
                    edit_link=edit_link,
                    event_type="end",
                    duration=duration,
                )
            )


def _add_sleeps(min_date, max_date, events, child=None):
    instances = _duration_instances_for_day(
        Sleep,
        min_date,
        max_date,
        child,
    )

    for instance in instances:
        details = []

        if instance.notes:
            details.append(instance.notes)

        edit_link = reverse("core:sleep-update", args=[instance.id])

        if _is_in_range(instance.start, min_date, max_date):
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

        if _is_in_range(instance.end, min_date, max_date):
            duration = None

            if instance.duration > timedelta(seconds=0):
                duration = duration_string(instance.duration)

            events.append(
                _build_timeline_event(
                    instance=instance,
                    event_time=instance.end,
                    message=_("%(child)s woke up.")
                    % {"child": instance.child.first_name},
                    details=details,
                    edit_link=edit_link,
                    event_type="end",
                    duration=duration,
                )
            )


def _get_feeding_instances(min_date, max_date, child=None):
    yesterday = min_date - timedelta(days=1)

    instances = (
        Feeding.objects.filter(
            Q(start__range=(yesterday, max_date)) | Q(end__range=(min_date, max_date))
        )
        .distinct()
        .order_by("start")
    )

    if child:
        instances = instances.filter(child=child)

    return instances


def _build_feeding_details(instance):
    details = []

    if instance.notes:
        details.append(instance.notes)

    if instance.amount:
        details.append(_("Amount") + ": " + str(instance.amount))

    return details


def _build_feeding_start_event(
    instance,
    details,
    edit_link,
    time_since_prev,
):
    return _build_timeline_event(
        instance=instance,
        event_time=instance.start,
        message=_("%(child)s started feeding.") % {"child": instance.child.first_name},
        details=details,
        edit_link=edit_link,
        event_type="start",
        time_since_prev=time_since_prev,
    )


def _build_feeding_end_event(instance, details, edit_link):
    return _build_timeline_event(
        instance=instance,
        event_time=instance.end,
        message=_("%(child)s finished feeding.") % {"child": instance.child.first_name},
        details=details,
        edit_link=edit_link,
        event_type="end",
        duration=duration_string(instance.duration),
    )


def _build_single_feeding_event(
    instance,
    details,
    edit_link,
    time_since_prev,
):
    return _build_timeline_event(
        instance=instance,
        event_time=instance.start,
        message=_("%(child)s had a feeding.") % {"child": instance.child.first_name},
        details=details,
        edit_link=edit_link,
        time_since_prev=time_since_prev,
    )


def _add_feedings(min_date, max_date, events, child=None):
    instances = _get_feeding_instances(
        min_date,
        max_date,
        child,
    )

    prev_start = None

    for instance in instances:
        time_since_prev = None

        if prev_start:
            time_since_prev = timesince.timesince(
                prev_start,
                now=instance.start,
            )

        prev_start = instance.start

        if instance.start < min_date and not _is_in_range(
            instance.end, min_date, max_date
        ):
            continue

        details = _build_feeding_details(instance)
        edit_link = reverse("core:feeding-update", args=[instance.id])

        if instance.duration > timedelta(seconds=0):
            if _is_in_range(instance.start, min_date, max_date):
                events.append(
                    _build_feeding_start_event(
                        instance,
                        details,
                        edit_link,
                        time_since_prev,
                    )
                )

            if _is_in_range(instance.end, min_date, max_date):
                events.append(
                    _build_feeding_end_event(
                        instance,
                        details,
                        edit_link,
                    )
                )

        elif _is_in_range(instance.start, min_date, max_date):
            events.append(
                _build_single_feeding_event(
                    instance,
                    details,
                    edit_link,
                    time_since_prev,
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
