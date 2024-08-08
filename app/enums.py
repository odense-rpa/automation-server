import enum

class WorkItemStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING_USER_ACTION = "pending user action"

class TargetTypeEnum(str, enum.Enum):
    PYTHON = 'python'
    BLUE_PRISM = 'blue_prism'
    UI_PATH = 'ui_path'
    POWER_AUTOMATE_DESKTOP = 'power_automate_desktop'

class SessionStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in progress"
    COMPLETED = "completed"
    FAILED = "failed"

    def can_transition_to(self, new_status: "SessionStatus") -> bool:
        transition_map = {
            SessionStatus.NEW: {SessionStatus.IN_PROGRESS},
            SessionStatus.IN_PROGRESS: {SessionStatus.COMPLETED, SessionStatus.FAILED},
            SessionStatus.COMPLETED: set(),
            SessionStatus.FAILED: set(),
        }
        return new_status in transition_map[self]
    
class TriggerType(str, enum.Enum):
    CRON = 'cron'
    WORKQUEUE = 'workqueue'
    DATE = 'date'