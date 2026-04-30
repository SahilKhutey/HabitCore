import random

DIFFICULTY_XP = {
    "Easy": 10,
    "Medium": 20,
    "Hard": 40
}

def calculate_xp_reward(streak: int, difficulty: str = "Medium", user_mode: str = "Consistency"):
    base_xp = DIFFICULTY_XP.get(difficulty, 20)
    
    # Speed Runner mode gets +25% base XP but lower streak bonuses
    if user_mode == "Speed":
        base_xp = int(base_xp * 1.25)
    
    bonus_xp = 0
    # Streak rewards (Consistency King gets double streak bonuses)
    streak_mult = 2.0 if user_mode == "Consistency" else 1.0
    
    if streak >= 30:
        bonus_xp = 50 * streak_mult
    elif streak >= 7:
        bonus_xp = 15 * streak_mult
    elif streak >= 3:
        bonus_xp = 5 * streak_mult
        
    total_xp = base_xp + bonus_xp
    
    # Random Bonus (10% chance)
    lucky_bonus = 0
    if random.random() < 0.1:
        lucky_bonus = 25
        
    return total_xp, lucky_bonus

def calculate_coin_reward(streak: int):
    base_coins = 5
    if streak >= 7:
        return base_coins + 10
    return base_coins

def calculate_level(xp: int):
    if xp == 0:
        return 1
    return int((xp / 100) ** 0.5) + 1
