from __future__ import annotations

import re
import pytest
from unittest.mock import MagicMock, patch

from magda.utils.logger import MagdaLogger
from magda.utils.logger.config import LoggerConfig


class PartialOutput(str):
    COLOR_REGEXP = r'\x1b'
    color = False

    def with_color(self) -> PartialOutput:
        self.color = True
        return self

    def __eq__(self, other: str):
        return self in other and (re.search(self.COLOR_REGEXP, other) is not None) == self.color


class TestMagdaLogger:
    @pytest.mark.parametrize(
        "log_level",
        ['info', 'debug', 'warn', 'critical', 'error']
    )
    @patch('magda.utils.logger.logger.print')
    def test_should_log_standard_message(self, mock, log_level):
        config = MagdaLogger.Config()
        logger = MagdaLogger.of(config)
        log_method = getattr(logger, log_level)
        message = 'Hello!'
        log_method(message)
        mock.assert_called_once_with(PartialOutput(message).with_color())

    @pytest.mark.parametrize(
        "log_level",
        ['info', 'debug', 'warn', 'critical', 'error']
    )
    @patch('magda.utils.logger.logger.print')
    def test_should_log_standard_message_without_colors(self, mock, log_level):
        config = MagdaLogger.Config(colors=False)
        logger = MagdaLogger.of(config)
        log_method = getattr(logger, log_level)
        message = 'Hello!'
        log_method(message)
        mock.assert_called_once_with(PartialOutput(message))

    @pytest.mark.parametrize(
        "log_level",
        ['info', 'debug', 'warn', 'critical', 'error']
    )
    @patch('magda.utils.logger.logger.print')
    def test_logger_should_be_disabled(self, mock, log_level):
        config = MagdaLogger.Config(enable=False)
        logger = MagdaLogger.of(config)
        log_method = getattr(logger, log_level)
        message = 'Hello!'
        log_method(message)
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

    @pytest.mark.parametrize(
        "log_level",
        ['info', 'debug', 'warn', 'critical', 'error']
    )
    @patch('magda.utils.logger.logger.print')
    @patch('magda.utils.logger.logger.getLogger')
    def test_logger_should_use_prints(self, logging_mock, print_mock, log_level):
        config = MagdaLogger.Config(output=MagdaLogger.Config.Output.STDOUT)
        logger = MagdaLogger.of(config)
        log_method = getattr(logger, log_level)
        message = 'Hello!'
        log_method(message)
        print_mock.assert_called_once_with(PartialOutput(message).with_color())
        logging_mock.assert_not_called()

    @pytest.mark.parametrize(
        "log_level",
        ['info', 'debug', 'warn', 'critical', 'error']
    )
    @patch('magda.utils.logger.logger.print')
    @patch('magda.utils.logger.logger.getLogger')
    def test_logger_should_use_native_logging(self, logging_mock, print_mock, log_level):
        runtime_logger_mock = MagicMock()
        logging_mock.return_value = runtime_logger_mock

        config = MagdaLogger.Config(output=MagdaLogger.Config.Output.LOGGING)
        logger = MagdaLogger.of(config)
        log_method = getattr(logger, log_level)
        message = 'Hello!'
        log_method(message)

        print_mock.assert_not_called()
        logging_mock.assert_called_once()
        getattr(
            runtime_logger_mock,
            log_level
        ).assert_called_once_with(PartialOutput(message).with_color())

    @pytest.mark.parametrize(
        "log_method,level_part",
        [
            ('info', LoggerConfig.Level.INFO.name),
            ('debug', LoggerConfig.Level.DEBUG.name),
            ('warn', LoggerConfig.Level.WARNING.name),
            ('critical', LoggerConfig.Level.CRITICAL.name),
            ('error', LoggerConfig.Level.ERROR.name)
        ]
    )
    @patch('magda.utils.logger.logger.print')
    def test_should_include_level_part_in_standard_logger(self, print_mock, log_method, level_part):
        config = MagdaLogger.Config(output=MagdaLogger.Config.Output.STDOUT)
        logger = MagdaLogger.of(config)
        log_method = getattr(logger, log_method)
        message = 'Hello!'
        log_method(message)
        print_mock.assert_called_once_with(PartialOutput(level_part).with_color())

    @pytest.mark.parametrize(
        "log_level",
        ['info', 'debug', 'warn', 'critical', 'error']
    )
    @patch('magda.utils.logger.logger.print')
    @patch('magda.utils.logger.logger.getLogger')
    def test_logger_should_use_custom_output(self, logging_mock, print_mock, log_level):
        output_mock = MagicMock()
        config = MagdaLogger.Config(output=output_mock)
        logger = MagdaLogger.of(config)
        log_method = getattr(logger, log_level)
        message = 'Hello!'
        log_method(message)

        print_mock.assert_not_called()
        logging_mock.assert_not_called()
        output_mock.assert_called_once_with(PartialOutput(message).with_color())

    @pytest.mark.parametrize(
        "log_level",
        ['info', 'debug', 'warn', 'critical', 'error']
    )
    @patch('magda.utils.logger.logger.print')
    @patch('magda.utils.logger.logger.getLogger')
    def test_logger_should_not_fail_with_non_callable_output(
        self,
        logging_mock,
        print_mock,
        log_level
    ):
        output_mock = 'Non-callable'
        config = MagdaLogger.Config(output=output_mock)
        logger = MagdaLogger.of(config)
        log_method = getattr(logger, log_level)
        message = 'Hello!'

        log_method(message)

        print_mock.assert_not_called()
        logging_mock.assert_not_called()

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
        request_name = 'RequestR1'
        request = MagdaLogger.Parts.Request(request_name)

        mock = MagicMock()
        config = MagdaLogger.Config(output=mock, format=[])
        logger = MagdaLogger.of(config).chain(request=request)

        message = 'Hello!'
        logger.info(message)

        mock.assert_called_once_with('')
