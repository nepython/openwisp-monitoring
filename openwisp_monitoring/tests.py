# Temporarily added to identify slow tests

from time import time
from unittest import TextTestResult

from django.test.runner import DiscoverRunner


class TimeLoggingTestResult(TextTestResult):
    def __init__(self, *args, **kwargs):
        self.slow_test_threshold = 0.3
        self.test_timings = []
        super().__init__(*args, **kwargs)

    def startTest(self, test):
        self._start_time = time()
        super().startTest(test)

    def addSuccess(self, test):
        elapsed = time() - self._start_time
        name = self.getDescription(test)
        self.test_timings.append((name, elapsed))
        super().addSuccess(test)

    def color(self, color):
        color_dict = {
            'white_bold': '37;1',
            'green_bold': '32;1',
            'yellow_bold': '33;1',
            'red_bold': '31;1',
            'reset': '0',
        }
        assert color in color_dict
        return f'\033[{color_dict[color]}m'

    def display_slow_tests(self):
        print(
            f'\n{self.color("white_bold")}These are your {self.color("yellow_bold")}culprit '
            f'{self.color("white_bold")}slow tests (>{self.slow_test_threshold}s)\n'
        )
        self._module = None
        slow_tests_counter = 0
        for name, elapsed in self.test_timings:
            if elapsed > self.slow_test_threshold:
                slow_tests_counter += 1
                name, module = name.split()
                if module != self._module:
                    self._module = module
                    print(f'{self.color("yellow_bold")}{module}{self.color("reset")}')
                color = (
                    self.color("red_bold") if elapsed > 1 else self.color("yellow_bold")
                )
                print(f'  ({color}{elapsed:.2f}s{self.color("reset")}) {name}')
        print(
            f'\n{self.color("white_bold")}Total slow tests detected: '
            f'{slow_tests_counter}{self.color("reset")}'
        )
        return self.test_timings

    def stopTestRun(self):
        self.display_slow_tests()
        super().stopTestRun()


class TimeLoggingTestRunner(DiscoverRunner):
    def get_resultclass(self):
        return TimeLoggingTestResult
