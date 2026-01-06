# -*- coding: utf-8 -*-

class TimeManager:
    def __init__(self, day_duration_seconds=300):  # 5 minutos = 300 segundos
        self.day_duration = day_duration_seconds
        self.current_time = 0  # em segundos
        self.current_day = 1
        self.is_paused = False
        
    def update(self, dt):
        """Atualiza o tempo"""
        if not self.is_paused:
            self.current_time += dt
            
            # Aqui ele verifica se passou um dia
            if self.current_time >= self.day_duration:
                self.current_time = 0
                self.current_day += 1
                return True  # Indica que um novo dia começou
        return False
    
    def get_time_of_day(self):
        """Retorna a hora do dia (0-1, onde 0 é início do dia, 1 é fim)"""
        return self.current_time / self.day_duration
    
    def pause(self):
        """Pausa o tempo"""
        self.is_paused = True
    
    def resume(self):
        """Retoma o tempo"""
        self.is_paused = False
    
    def set_day_duration(self, seconds):
        """Define a duração de um dia em segundos"""
        self.day_duration = seconds
    
    def get_formatted_time(self):
        """Retorna o tempo formatado"""
        hours = int((self.current_time / self.day_duration) * 24)
        minutes = int(((self.current_time / self.day_duration) * 24 * 60) % 60)
        return f"{self.current_day}, {hours:02d}:{minutes:02d}"