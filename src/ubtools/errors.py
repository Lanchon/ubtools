class UBootError(RuntimeError):
    pass


class UBootCommunicationError(UBootError):
    pass


class UBootUnexpectedPromptError(UBootCommunicationError):
    def __init__(self, message: str, prompt: str | None) -> None:
        super().__init__(message)
        self.prompt = prompt

    def __str__(self) -> str:
        parts = [super().__str__()]
        if self.prompt is not None:
            parts.append(f"prompt={self.prompt!r}")
        return "\n\t".join(parts)


class UBootCommandError(UBootError):
    def __init__(self, message: str, command: str | None = None, output: list[str] | None = None,
                 exit_code: int | None = None) -> None:
        super().__init__(message)
        self.command = command
        self.output = output
        self.exit_code = exit_code

    def __str__(self) -> str:
        parts = [super().__str__()]
        if self.command is not None:
            parts.append(f"command={self.command!r}")
        if self.output is not None:
            parts.append(f"output={self.output!r}")
        if self.exit_code is not None:
            parts.append(f"exit_code={self.exit_code}")
        return "\n\t".join(parts)


class UBootCommandExitCodeError(UBootCommandError):
    def __init__(self, command: str | None = None, output: list[str] | None = None,
                 exit_code: int | None = None) -> None:
        super().__init__(f"Command failed with exit code {exit_code}",
                         command=command, output=output, exit_code=exit_code)


class UBootCommandOutputError(UBootCommandError):
    pass

