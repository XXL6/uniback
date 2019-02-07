import re


class ProgressTracker:

    current_progress = 0.0

    def get_current_progress(self):
        return self.current_progress

    def set_regex(self, regex):
        self.regex = regex

    def set_progress(self, input_string):
        # we use regex to try and parse out the potential progress strings
        # that might show up in the application
        try:
            parsed_string = re.search(self.regex, input_string)
        except AttributeError:
            raise "Attempt to set the progress was made, but regex \
                was not defined."
        if parsed_string:
            try:
                current_progress = float(parsed_string.group())
            except ValueError:
                return
            self.current_progress = current_progress

    def reset_progress(self):
        self.current_progress = 0.0
