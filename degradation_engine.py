import time
import random
from collections import deque
from config import *

class DegradationEngine:
    def __init__(self, player_paddle, ai_paddle):
        # queue to hold inputs
        self.action_queue = deque()
        self.immediate_queue = []
        self.latency = 0
        self.loss_percent = 0.0

        self.player_paddle = player_paddle
        self.ai_paddle = ai_paddle

        self.packets_sent = 0
        self.packets_lost = 0

    def set_parameters(self, latency, loss_percent):
        """Update degradation params from slider values"""
        self.latency = latency
        self.loss_percent = loss_percent

    def get_max_jitter(self):
        """Calculate max jitter based off latency slider & config JITTER_MAP"""
        max_jitter = 0
        for threshold, jitter_val in sorted(JITTER_MAP.items()):
            if self.latency >= threshold:
                max_jitter = jitter_val
        return max_jitter

    def queue_input(self, target_paddle, data):
        """
        Receive input and queue it if it passes loss check.
        Handle packet loss.
        Handle latency and jitter.
        """
        self.packets_sent += 1

        # check for packet loss
        if random.random() * 100 < self.loss_percent:
            self.packets_lost += 1
            return None  # drop packet

        # no delay for user at latency = 0
        if target_paddle is self.player_paddle and self.latency <= 5:
            action = {
                'target' : target_paddle,
                'data' : data,
                'time_due' : 0
            }
            self.immediate_queue.append(action)
            return

        else:
            # add ai imperfection
            if target_paddle == self.ai_paddle:
                ai_delay_seconds = AI_REACTION_TIME / 1000.0
            else:
                ai_delay_seconds = 0

            # apply latency with random jitter
            base_delay_seconds = self.latency / 1000.0
            # don't have jitter for no latency
            if self.latency > 0:
                jitter_delay_seconds = (random.uniform(0, self.get_max_jitter()) / 1000.0)
            else:
                jitter_delay_seconds = 0

            total_delay_seconds = (base_delay_seconds + jitter_delay_seconds + ai_delay_seconds)
            time_due = time.time() + total_delay_seconds
        
        # queue action
        action = {
            'target' : target_paddle,
            'data' : data,  # direction (-1 or 1)
            'time_due' : time_due
        }
        self.action_queue.append(action)

    def get_due_actions(self):
        """Return list of all past due actions. Remove them from queue"""
        released_actions = []

        # first get immediate
        if self.immediate_queue:
            released_actions.extend(self.immediate_queue)
            self.immediate_queue.clear()

        # pop oldest action if its due
        current_time = time.time()
        while self.action_queue and self.action_queue[0]['time_due'] <= current_time:
            released_actions.append(self.action_queue.popleft())
        return released_actions

    def get_stats(self):
        """Return current stats for display"""
        # calculate loss rate
        total = self.packets_sent
        lost = self.packets_lost
        loss_rate = (lost / total) * 100 if total > 0 else 0.0

        return {
            'sent' : total,
            'received' : total - lost,
            'lost' : lost,
            'loss rate' : loss_rate
        }

    def reset_stats(self):
        """Reset packet counters and clear action queue"""
        self.packets_sent = 0
        self.packets_lost = 0
        self.action_queue.clear()
        self.immediate_queue.clear()
