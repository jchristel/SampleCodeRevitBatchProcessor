from duHast.Utilities.console_out import output
from duHast.Utilities.Objects.base import Base


class FailureHandlingConfig(Base):
    def __init__(
        self,
        roll_back_on_warning=False,
        print_warnings=False,
        roll_back_on_error=False,
        print_errors=False,
        set_forced_modal_handling=True,
        set_clear_after_rollback=True,
        output_function=output,
    ):
        self.roll_back_on_warning = roll_back_on_warning
        self.print_warnings = print_warnings
        self.roll_back_on_error = roll_back_on_error
        self.print_errors = print_errors
        self.allowable_failures = None
        self.set_forced_modal_handling = set_forced_modal_handling
        self.set_clear_after_rollback = set_clear_after_rollback
        self.output_function = output_function
