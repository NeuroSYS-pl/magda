from __future__ import annotations

import re
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch

from magda.utils.logger import MagdaLogger


class PartialOutput(str):
    COLOR_REGEXP = r'\x1b'
    color = False

    def with_color(self) -> PartialOutput:
        self.color = True
        return self

    def __eq__(self, other: str):
        return self in other and (re.search(self.COLOR_REGEXP, other) is not None) == self.color


class TestMagdaLogger(TestCase):
    @patch('magda.utils.logger.logger.print')
    def test_should_log_standard_message(self, mock):
        config = MagdaLogger.Config()
        logger = MagdaLogger.of(config)
        message = 'Hello!'
        logger.info(message)
        mock.assert_called_once_with(PartialOutput(message).with_color())

    @patch('magda.utils.logger.logger.print')
    def test_should_log_standard_message_without_colors(self, mock):
        config = MagdaLogger.Config(colors=False)
        logger = MagdaLogger.of(config)
        message = 'Hello!'
        logger.info(message)
        mock.assert_called_once_with(PartialOutput(message))

    @patch('magda.utils.logger.logger.print')
    def test_logger_should_be_disabled(self, mock):
        config = MagdaLogger.Config(enable=False)
        logger = MagdaLogger.of(config)
        message = 'Hello!'
        logger.info(message)
        mock.assert_not_called()

    @patch('magda.utils.logger.logger.print')
    def test_should_log_event(self, mock):
        config = MagdaLogger.Config()
        logger = MagdaLogger.of(config)
        message = 'TestEvent'
        logger.event(message)
        mock.assert_called_once_with(PartialOutput(message).with_color())

    @patch('magda.utils.logger.logger.print')
    def test_should_skip_events(self, mock):
        config = MagdaLogger.Config(log_events=False)
        logger = MagdaLogger.of(config)
        message = 'Hello!'
        event = 'TestEvent'
        logger.info(message)
        logger.event(event)
        mock.assert_called_once_with(PartialOutput(message).with_color())

    @patch('magda.utils.logger.logger.print')
    def test_logger_should_use_prints(self, print_mock):
        with self.assertLogs(level=logging.INFO) as log:
            config = MagdaLogger.Config(output=MagdaLogger.Config.Output.STDOUT)
            logger = MagdaLogger.of(config)
            message = 'Hello!'
            logger.info(message)

            print_mock.assert_called_once_with(PartialOutput(message).with_color())
            self.assertEqual(len(log.output), 0)

    @patch('magda.utils.logger.logger.print')
    def test_logger_should_use_native_logging(self, print_mock):
        with self.assertLogs(level=logging.INFO) as log:
            config = MagdaLogger.Config(output=MagdaLogger.Config.Output.LOGGING)
            logger = MagdaLogger.of(config)
            message = 'Hello!'
            logger.info(message)

            print_mock.assert_not_called()
            self.assertEqual(len(log.output), 1)
            self.assertIn(PartialOutput(message).with_color(), log.output[0])

    @patch('magda.utils.logger.logger.print')
    def test_logger_should_use_custom_output(self, print_mock):
        with self.assertLogs(level=logging.INFO) as log:
            mock = MagicMock()
            config = MagdaLogger.Config(output=mock)
            logger = MagdaLogger.of(config)
            message = 'Hello!'
            logger.info(message)

            print_mock.assert_not_called()
            self.assertEqual(len(log.output), 0)
            mock.assert_called_once_with(PartialOutput(message).with_color())

    @patch('magda.utils.logger.logger.print')
    def test_logger_should_not_fail_with_non_callable_output(self, print_mock):
        with self.assertLogs(level=logging.INFO) as log:
            mock = 'Non-callable'
            config = MagdaLogger.Config(output=mock)
            logger = MagdaLogger.of(config)
            message = 'Hello!'

            logger.info(message)

            print_mock.assert_not_called()
            self.assertEqual(len(log.output), 0)

    def test_loggers_should_be_chained(self):
        request_name = 'RequestR1'
        request = MagdaLogger.Parts.Request(request_name)

        mock = MagicMock()
        config = MagdaLogger.Config(output=mock)
        logger = MagdaLogger.of(config).chain(request=request)

        message = 'Hello!'
        logger.info(message)

        mock.assert_called_once_with(PartialOutput(message).with_color())
        mock.assert_called_once_with(PartialOutput(request_name).with_color())

    def test_format_should_be_overriden(self):
        request = MagdaLogger.Parts.Request('RequestR1')

        mock = MagicMock()
        config = MagdaLogger.Config(output=mock, format=[])
        logger = MagdaLogger.of(config).chain(request=request)

        logger.info('Hello!')
        mock.assert_called_once_with('')