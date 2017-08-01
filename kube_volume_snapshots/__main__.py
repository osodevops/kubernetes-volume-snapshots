#!/usr/bin/env python

from snapshot import Snapshot


def main():
    snapshot = Snapshot()
    snapshot.process_pods()


if __name__ == '__main__':
    main()

