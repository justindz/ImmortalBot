def max_buffed_damage(max_base_damage: float, blood_drinker: float, blood_thirst: float):
    return max_base_damage + blood_drinker + blood_thirst


def min_buffed_damage(max_buffed_damage: float, weapon_variance: float):
    return max_buffed_damage * (1.0 - weapon_variance)


def starting_weapon_variance(min_base_damage: float, max_base_damage: float):
    return (max_base_damage - min_base_damage) / max_base_damage


def starting_average_damage(min_base_damage: float, max_base_damage: float, blood_drinker: float, blood_thirst: float, critical_hit_rate=0.1, critical_hit_mod=2.0, damage_rating_percent=1.05):
    max_buffed = max_buffed_damage(max_base_damage, blood_drinker, blood_thirst)
    min_buffed = min_buffed_damage(max_buffed, starting_weapon_variance(min_base_damage, max_base_damage))
    return round(max_buffed * critical_hit_rate * critical_hit_mod * critical_hit_damage_rating_percent() + (1.0 - critical_hit_rate) * ((max_buffed + min_buffed) / 2.0) * damage_rating_percent, 2)


def critical_hit_damage_rating_percent(damage_rating=5.0, critical_hit_damage_rating=3.0):
    return (100.0 + damage_rating + critical_hit_damage_rating) / 100.0


def average_damage(min_base_damage, max_base_damage, blood_thirst, i, critical_hit_mod=2.0, blood_drinker=24.0, damage_rating_percent=1.05, critical_hit_rate=0.1, number_of_tinks=9.0):
    return round(damage_rating_percent * (((1.0 - (1.0 - min_base_damage / max_base_damage) * pow(0.8, number_of_tinks - float(i))) * (max_base_damage + blood_drinker + blood_thirst + float(i)) + (max_base_damage + blood_drinker + blood_thirst + float(i))) / 2.0) + (max_base_damage + blood_drinker + blood_thirst + float(i)) * critical_hit_rate * critical_hit_mod * critical_hit_damage_rating_percent(), 2)
