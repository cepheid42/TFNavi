import time


class Timer:
    def __init__(self, name):
        self.name = name

        cpu_time = time.process_time()
        wall_time = time.time()

        self.t0 = [cpu_time, wall_time]
        self.t = [cpu_time, wall_time]
        self.splits = []

        self.cpu_tot = 0
        self.wall_tot = 0

    def update_time(self, new_time):
        self.t = new_time

    def elapsed(self):
        cpu_time = time.process_time()
        wall_time = time.time()

        self.splits.append((cpu_time - self.t[0], wall_time - self.t[1]))

        return [cpu_time, wall_time]

    def reset(self):
        cpu_time = time.process_time()
        wall_time = time.time()

        self.t0 = [cpu_time, wall_time]
        self.t = [cpu_time, wall_time]
        self.splits = []

    def sum_splits(self):
        cpu_tot = 0.0
        wall_tot = 0.0

        for split in self.splits:
            cpu_tot += split[0]
            wall_tot += split[1]

        return cpu_tot, wall_tot

    def stop(self):
        self.cpu_tot, self.wall_tot = self.sum_splits()

    def __str__(self):
        return f'{self.name:<15.20s} {self.cpu_tot:^12.6f} {self.wall_tot:^12.6f}'


class Timers:
    def __init__(self, *args):
        self.timers = {name: Timer(name) for name in args}
        self.total_timer = Timer('Total')

    def elapsed(self, name):
        new_t = self.timers[name].elapsed()

        for name, timer in self.timers.items():
            timer.update_time(new_t)

    def reset(self, *names):
        # If no names supplied, reset ALL timers
        if not names:
            names = self.timers.keys()

        for name in names:
            self.timers[name].reset()

    def print(self):
        test_cpu = 0
        test_wall = 0

        for name, timer in self.timers.items():
            timer.stop()
            test_cpu += timer.cpu_tot
            test_wall += timer.wall_tot

        print("#" * 50)
        print(f'{"Timer":<15.20s} {"CPU sec":^12.10s} {"Wall sec":^12.10s}')
        print("-" * 50)

        for name in self.timers.keys():
            print(self.timers[name])

        total_cpu = time.process_time() - self.total_timer.t0[0]
        total_wall = time.time() - self.total_timer.t0[1]
        print(f'{self.total_timer.name:<15.20s} {total_cpu:^12.6f} {total_wall:^12.6f}')
        print("#" * 50)

    def file_print(self, f):
        test_cpu = 0
        test_wall = 0

        for name, timer in self.timers.items():
            timer.stop()
            test_cpu += timer.cpu_tot
            test_wall += timer.wall_tot

        print(f'{"Timer":<15.20s} {"CPU sec":^12.10s} {"Wall sec":^12.10s}', file=f)

        for name in self.timers.keys():
            print(self.timers[name], file=f)

        total_cpu = time.process_time() - self.total_timer.t0[0]
        total_wall = time.time() - self.total_timer.t0[1]
        print(f'{self.total_timer.name:<15.20s} {total_cpu:^12.6f} {total_wall:^12.6f}', file=f)

