"""Command-line entry point."""

from dns_updater.app import main


def run() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    run()
