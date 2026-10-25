"""Packaging entry point; normal launches use the unchanged application."""
import sys

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--acceptance-test":
        from frozen_acceptance import main

        raise SystemExit(main(sys.argv[2]))
    from dss.__main__ import main

    raise SystemExit(main())
