"""Hard-constraint helpers for the CP-SAT block optimizer."""

from datetime import datetime

from app.optimizer.scoring import ExistingBlock, ResourceCandidate, TaskCandidate, WindowCandidate
from app.utils.time_utils import overlaps


def window_fits_task(task: TaskCandidate, window: WindowCandidate) -> bool:
    if task.section != window.section:
        return False
    length = int((window.end - window.start).total_seconds() // 60)
    return length >= task.duration_minutes


def resource_matches(task: TaskCandidate, resource: ResourceCandidate) -> bool:
    if not resource.available:
        return False
    if task.resource_type and resource.resource_type != task.resource_type:
        return False
    if resource.section not in {task.section, "*"}:
        return False
    return True


def window_hits_existing_block(window: WindowCandidate, blocks: list[ExistingBlock]) -> bool:
    for block in blocks:
        if block.section != window.section:
            continue
        if overlaps(window.start, window.end, block.start, block.end):
            return True
    return False


def window_has_train_conflict(window: WindowCandidate) -> bool:
    return window.train_conflicts > 0
