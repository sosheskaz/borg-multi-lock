# borg-multi-lock
A Standalone Python Script I made for acquiring multiple exclusive borg locks.

## Why?

I back up my borg repositories using snapshots and rclone. In order for this to be effective, we need the borg repository to be in a stable state - that is, we do not want a backup or prune to be in progress while the process runs.

Because:

* offsite replication can take several hours
* my borg backups run hourly
* borg is a client-driven backup system

I needed a centralized way to prevent borg backups from running against a set of repositories on the file system.

## How

`borg with-lock` almost accomplishes what I need, but it lacks the ability to gather multiple locks simultaneously, and even if done serially there are potentially timing issues.

Borg has an internal `Lock` mechanism which functions like a mutex. We acquire this lock for multiple repositories simultaneously.

This lock is respected across physical machines, so long as they are all writeable on a file system or virtual file system. This does not work over SSH like borg.

That is, this script expects to be run from the machine hosting the borg repositories, but will prevent any clients from using the repositories (unless they explicitly break the lock).

## Usage

```bash
sudo ./borg-multi-lock.py -r /path/to/repo/1 /path/to/repo/2 /path/to/repo/N -- echo "This command will be run only while borg locks for all specified repos have been acquired"
```
