from retro_data_structures.formats.script_object import ScriptInstanceHelper
from retro_data_structures.formats.script_layer import ScriptLayerHelper
from retro_data_structures.game_check import Game
from open_prime_rando.echoes.enemy_attribute_randomizer.CommonStructs import *
from open_prime_rando.echoes.enemy_attribute_randomizer.__init__ import Randomize_Values
from open_prime_rando.echoes.asset_ids.agon_wastes import *
from open_prime_rando.echoes.asset_ids.great_temple import *
from open_prime_rando.echoes.asset_ids.sanctuary_fortress import *
from open_prime_rando.echoes.asset_ids.temple_grounds import *
from open_prime_rando.echoes.asset_ids.torvus_bog import *

import copy

import random

from open_prime_rando.patcher_editor import PatcherEditor

def Enemy_Eye_Ball(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Rand_Speed = 1.0
    Enemy_props: Enemy = Enemy.get_properties()
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.close_time /= Rand_Speed
    Enemy_props.fire_wait_time /= Rand_Speed
    DAMAGE_INFO(Enemy_props.ray_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    COLOR(Enemy_props.laser_inner_color, Enemy.id, rng)
    COLOR(Enemy_props.laser_outer_color, Enemy.id, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Blogg(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] < 0.1:
        Data_Range["SC_Low"] = 0.1
    if Data_Range["SC_High"] > 2.0:
        Data_Range["SC_High"] = 2.0
    if Data_Range["SC_Low"] > Data_Range["SC_High"]:
        Data_Range["SC_Low"] = Data_Range["SC_High"]
    if Data_Range["SC_High"] < Data_Range["SC_Low"]:
        Data_Range["SC_High"] = Data_Range["SC_Low"]
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Rand_Speed = 1/((Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.projectile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.body_damage_multiplier *= Rand_Damage
    Enemy_props.mouth_damage_multiplier *= Rand_Damage
    DAMAGE_VULNERABILITY(Enemy_props.armor_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    #Enemy_props.charge_damage_radius
    Enemy_props.charge_damage *= Rand_Damage
    Enemy_props.bite_damage *= Rand_Damage
    Enemy_props.ball_spit_damage *= Rand_Damage
    Enemy_props.charge_turn_speed *= Rand_Speed
    Enemy_props.charge_speed_multiplier *= Rand_Speed
    ING_POSSESSION_DATA(Enemy_props.ing_possession_data, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.ing_possessed_armor_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

    if Enemy.id == 0x08390104:
        TEMP(editor, 'PLATFORM', MAIN_HYDROCHAMBER_MREA, 0x1039013d, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'PLATFORM', MAIN_HYDROCHAMBER_MREA, 0x1039014e, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)

def Enemy_Flyer_Swarm(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    #EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    BASIC_SWARM_PROPERTIES(Enemy_props.basic_swarm_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.roll_upright_speed *= Rand_Speed
    Enemy.set_properties(Enemy_props)

def Enemy_Glowbug(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.attack_duration /= Rand_Speed
    Enemy_props.attack_telegraph_duration /= Rand_Speed
    Enemy.set_properties(Enemy_props)

def Enemy_Lumite(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.small_shot_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.big_shot_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Mystery_Flyer(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.mystery_flyer_properties.shot_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.mystery_flyer_properties.hover_speed *= Rand_Speed
    Enemy.set_properties(Enemy_props)

def Enemy_Shrieker(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.buried_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.damage_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.projectile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.melee_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.melee_attack_time_variation /= Rand_Speed
    Enemy_props.dodge_time /= Rand_Speed
    Enemy_props.visibility_change_time = Rand_Speed
    Enemy.set_properties(Enemy_props)

def Enemy_Metaree(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] > 1.8:
        Data_Range["SC_Low"] = 1.8
    if Data_Range["SC_High"] > 1.8:
        Data_Range["SC_High"] = 1.8
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.radius_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.attack_speed *= Rand_Speed
    Enemy_props.drop_delay /= Rand_Speed
    Enemy_props.halt_delay /= Rand_Speed
    Enemy_props.launch_speed *= Rand_Speed
    Enemy.set_properties(Enemy_props)

def Enemy_Shredder(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.data.explosion_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.data.min_life_time /= Rand_Speed
    Enemy_props.data.max_life_time /= Rand_Speed
    Enemy_props.data.normal_knockback *= Rand_KnockBack
    Enemy_props.data.heavy_knockback *= Rand_KnockBack
    Enemy_props.data.knockback_decline *= Rand_KnockBack
    Enemy.set_properties(Enemy_props)

def Enemy_Pillbug(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.floor_turn_speed *= Rand_Speed
    DAMAGE_VULNERABILITY(Enemy_props.damage_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.wander_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Brizgee(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.wall_turn_speed *= Rand_Speed
    Enemy_props.floor_turn_speed *= Rand_Speed
    Enemy_props.down_turn_speed *= Rand_Speed
    DAMAGE_VULNERABILITY(Enemy_props.shell_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.shell_health *= Rand_Health
    DAMAGE_INFO(Enemy_props.shell_contact_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.poison_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.poison_time /= Rand_Speed
    Enemy.set_properties(Enemy_props)

def Enemy_Kralee(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.wall_turn_speed *= Rand_Speed
    Enemy_props.floor_turn_speed *= Rand_Speed
    Enemy_props.down_turn_speed *= Rand_Speed
    Enemy_props.warp_in_time /= Rand_Speed
    Enemy_props.warp_out_time /= Rand_Speed
    Enemy_props.visible_time /= Rand_Speed
    Enemy_props.invisible_time /= Rand_Speed
    #Enemy_props.warp_attack_radius
    Enemy_props.warp_attack_knockback *= Rand_KnockBack
    Enemy_props.warp_attack_damage *= Rand_Damage
    Enemy_props.anim_speed_scalar *= (Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3

    Enemy.set_properties(Enemy_props)

def Enemy_Plant_Scarab_Swarm(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    BASIC_SWARM_PROPERTIES(Enemy_props.basic_swarm_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.into_attack_speed *= Rand_Speed
    Enemy_props.attack_speed *= Rand_Speed
    Enemy_props.grenade_launch_speed *= Rand_Speed
    DAMAGE_INFO(Enemy_props.grenade_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Krocuss(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.wall_turn_speed *= Rand_Speed
    Enemy_props.floor_turn_speed *= Rand_Speed
    Enemy_props.down_turn_speed *= Rand_Speed
    Enemy_props.anim_speed_scalar *= (Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3
    DAMAGE_VULNERABILITY(Enemy_props.shell_closed_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Crystallite(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.wall_turn_speed *= Rand_Speed
    Enemy_props.floor_turn_speed *= Rand_Speed
    Enemy_props.down_turn_speed *= Rand_Speed
    Enemy_props.stun_time /= Rand_Speed
    Enemy.set_properties(Enemy_props)

def Enemy_Sandworm(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] < 0.05:
        Data_Range["SC_Low"] = 0.05
    if Data_Range["SC_High"] > 2.0:
        Data_Range["SC_High"] = 2.0
    if Data_Range["SC_Low"] > Data_Range["SC_High"]:
        Data_Range["SC_Low"] = Data_Range["SC_High"]
    if Data_Range["SC_High"] < Data_Range["SC_Low"]:
        Data_Range["SC_High"] = Data_Range["SC_Low"]
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    if Enemy.id == 0x081a009c and ((Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3) > 1.0:
        Rand_Speed = 1/((Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    #Enemy_props.pincer_scale *= (Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3
    DAMAGE_INFO(Enemy_props.projectile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.morphball_toss_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.pincer_swipe_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.pursuit_frustration_timer /= Rand_Speed
    DAMAGE_INFO(Enemy_props.ing_boss_bomb_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    SANDWORM_STRUCT(Enemy_props.sandworm_struct_0xb8c15f15, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    SANDWORM_STRUCT(Enemy_props.sandworm_struct_0xce246628, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    SANDWORM_STRUCT(Enemy_props.sandworm_struct_0x55578cfc, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    SANDWORM_STRUCT(Enemy_props.sandworm_struct_0x23ee1452, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    SANDWORM_STRUCT(Enemy_props.sandworm_struct_0xb89dfe86, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_POSSESSION_DATA(Enemy_props.ing_possession_data, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Grenchler(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] < 0.2:
        Data_Range["SC_Low"] = 0.2
    if Data_Range["SC_High"] > 2.0:
        Data_Range["SC_High"] = 2.0
    if Data_Range["SC_Low"] > Data_Range["SC_High"]:
        Data_Range["SC_Low"] = Data_Range["SC_High"]
    if Data_Range["SC_High"] < Data_Range["SC_Low"]:
        Data_Range["SC_High"] = Data_Range["SC_Low"]
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    if Enemy.id == 0x0c3b003d:
        if Rand_Speed > 1.75:
            if Data_Range["SP_Low"] > 1.75:
                Data_Range["SP_Low"] = 1.75
            if Data_Range["SP_High"] > 1.75:
                Data_Range["SP_High"] = 1.75
            Rand_Speed = Randomize_Values(rng, Data_Range)[2]
        TEMP(editor, 'ACTOR', SACRIFICIAL_CHAMBER_MREA, 0x0c3b01f6, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    #print(Rand_Scale)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_0x04d51e3a *= Rand_Health # Health value that when reached, the shell breaks
    DAMAGE_VULNERABILITY(Enemy_props.damage_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.bite_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.beam_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.burst_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_0xfc6f199d *= Rand_Health # Grapple Guardians 'yellow' health
    DAMAGE_INFO(Enemy_props.grapple_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.damage_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_POSSESSION_DATA(Enemy_props.ing_possession_data, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)
    
def Enemy_Sporb_Base(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] < 0.05:
        Data_Range["SC_Low"] = 0.05
    if Data_Range["SC_High"] > 2.0:
        Data_Range["SC_High"] = 2.0
    if Data_Range["SC_Low"] > Data_Range["SC_High"]:
        Data_Range["SC_Low"] = Data_Range["SC_High"]
    if Data_Range["SC_High"] < Data_Range["SC_Low"]:
        Data_Range["SC_High"] = Data_Range["SC_Low"]
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_0x95e7a2c2 /= Rand_Speed #Min of range for random delay between attacks
    Enemy_props.unknown_0x76ba1c18 /= Rand_Speed #Max of range for random delay between attacks
    Enemy_props.grabber_out_acceleration *= Rand_Speed
    Enemy_props.grabber_in_acceleration *= Rand_Speed
    Enemy_props.grabber_attach_time /= Rand_Speed
    #Enemy_props.spit_force
    Enemy_props.spit_damage *= Rand_Damage
    Enemy_props.grab_damage *= Rand_Damage
    DAMAGE_INFO(Enemy_props.power_bomb_projectile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng) #consider making radius smaller depending on speed
    Enemy_props.unknown_0x6d4e0f5a /= Rand_Speed #Delay before explosion once the power bomb hits the ground/wall
    POWER_BOMB_GUARDIAN_STAGE_PROPERTIES(Enemy_props.power_bomb_guardian_stage_properties_0x510dba97, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    POWER_BOMB_GUARDIAN_STAGE_PROPERTIES(Enemy_props.power_bomb_guardian_stage_properties_0x0b6c85f7, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    POWER_BOMB_GUARDIAN_STAGE_PROPERTIES(Enemy_props.power_bomb_guardian_stage_properties_0x8b9c92e8, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    POWER_BOMB_GUARDIAN_STAGE_PROPERTIES(Enemy_props.power_bomb_guardian_stage_properties_0xbfaefb37, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Splinter(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Enemy.id == 0x080200ff:
        if Data_Range["SC_Low"] < 0.05:
            Data_Range["SC_Low"] = 0.05
        if Data_Range["SC_High"] > 2.5:
            Data_Range["SC_High"] = 2.5
        if Data_Range["SC_Low"] > Data_Range["SC_High"]:
            Data_Range["SC_Low"] = Data_Range["SC_High"]
        if Data_Range["SC_High"] < Data_Range["SC_Low"]:
            Data_Range["SC_High"] = Data_Range["SC_Low"]
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    if Enemy.id == 0x082700c4 or Enemy.id == 0x082700c3:
        Rand_Speed = 1.0
    elif Enemy.id == 0x080202ab:
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x14020218, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x1402023B, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x14020263, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x1402020f, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    elif Enemy.id == 0x0802029c:
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x14020296, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x14020292, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x14020209, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x14020204, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x140201fe, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x1402021d, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    elif Enemy.id == 0x0802029f:
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x14020226, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x14020217, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x1402022f, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x1402023f, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    elif Enemy.id == 0x0802029e:
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x14020201, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x1402024b, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x1402028b, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x1402022D, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x14020260, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    elif Enemy.id == 0x0802029d:
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x1402020a, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x14020285, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x14020254, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    if Enemy.id == 0x080200ff:
        Enemy_props.unknown_0x72edeb7d *= Rand_Health
        EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng, 0.05, 2.5)
        TEMP(editor, 'ACTOR', TEMPLE_SANCTUARY_MREA, 0x1002000f, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'PLATFORM', TEMPLE_SANCTUARY_MREA, 0x08020104, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'PLATFORM', TEMPLE_SANCTUARY_MREA, 0x08020103, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    else:
        EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.attack_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.damage_info_0x4436a388, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_POSSESSION_DATA(Enemy_props.ing_possession_data, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_0x51be00d3 /= Rand_Speed #Min_delay to attack
    Enemy_props.unknown_0xb7deaf32 /= Rand_Speed #Max_delay to attack
    Enemy.set_properties(Enemy_props)

def Enemy_Atomic_Alpha(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.bomb_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.bomb_drop_delay /= Rand_Speed
    Enemy_props.bomb_reappear_delay /= Rand_Speed
    Enemy_props.bomb_reappear_time /= Rand_Speed
    Enemy.set_properties(Enemy_props)

def Enemy_Tryclops(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    #EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    #Enemy_props.attract_force
    #Enemy_props.shot_force
    Enemy.set_properties(Enemy_props)

def Enemy_Atomic_Beta(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] > 1.75:
        Data_Range["SC_Low"] = 1.75
    if Data_Range["SC_High"] > 1.75:
        Data_Range["SC_High"] = 1.75
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.beam_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.beam_fade_time /= Rand_Speed
    Enemy_props.hover_speed *= Rand_Speed
    DAMAGE_VULNERABILITY(Enemy_props.frozen_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.normal_rotate_speed *= Rand_Speed
    Enemy_props.charging_rotate_speed *= Rand_Speed
    Enemy_props.speed_change_rate /= Rand_Speed
    Enemy_props.damage_delay /= Rand_Speed
    Enemy.set_properties(Enemy_props)

def Enemy_Metaree_Swarm(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    BASIC_SWARM_PROPERTIES(Enemy_props.basic_swarm_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.into_attack_speed *= Rand_Speed
    Enemy_props.attack_speed *= Rand_Speed
    Enemy.set_properties(Enemy_props)

def Enemy_Rezbit(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.rezbit_data.shield_down_time /= Rand_Speed
    Enemy_props.rezbit_data.shield_up_time /= Rand_Speed
    Enemy_props.rezbit_data.unknown_0x70e597d4 /= Rand_Speed # delay between sidestepping
    Enemy_props.rezbit_data.unknown_0x6fbc1bf9 /= Rand_Speed # Delay between attacks
    DAMAGE_INFO(Enemy_props.rezbit_data.energy_bolt_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.rezbit_data.energy_bolt_attack_duration /= Rand_Speed
    Enemy_props.rezbit_data.unknown_0x28944183 /= Rand_Speed # Related to above
    Enemy_props.rezbit_data.unknown_0xc7a69a59 /= Rand_Speed # Dealy between shots
    Enemy_props.rezbit_data.virus_attack_time /= Rand_Speed
    DAMAGE_INFO(Enemy_props.rezbit_data.virus_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.rezbit_data.cutting_laser_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PLASMA_BEAM_INFO(Enemy_props.rezbit_data.cutting_laser_beam_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.rezbit_data.shield_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Octapede_Segment(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    #EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.wall_turn_speed *= Rand_Speed
    Enemy_props.floor_turn_speed *= Rand_Speed
    Enemy_props.down_turn_speed *= Rand_Speed
    Enemy_props.anim_speed_scalar *= (Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3
    DAMAGE_INFO(Enemy_props.explosion_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_AI_Manned_Turret(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_struct3.horiz_speed *= Rand_Speed
    Enemy_props.unknown_struct3.vert_speed *= Rand_Speed
    Enemy_props.unknown_struct3.fire_rate /= Rand_Speed
    Enemy_props.unknown_struct3.attack_leash_timer /= Rand_Speed
    DAMAGE_INFO(Enemy_props.unknown_struct3.weapon_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    HEALTH(Enemy_props.unknown_struct3.health, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.unknown_struct3.vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)
    if Enemy.id == 0x081d0055:
        TEMP(editor, 'ACTOR', CENTRAL_MINING_STATION_MREA, 0x081d005f, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'PLATFORM', CENTRAL_MINING_STATION_MREA, 0x081d005e, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'PLATFORM', CENTRAL_MINING_STATION_MREA, 0x081d0054, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', CENTRAL_MINING_STATION_MREA, 0x081d005c, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', CENTRAL_MINING_STATION_MREA, 0x081d0056, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)        
    elif Enemy.id == 0x081d0238:
        TEMP(editor, 'ACTOR', CENTRAL_MINING_STATION_MREA, 0x081d024b, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'PLATFORM', CENTRAL_MINING_STATION_MREA, 0x081d0249, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'PLATFORM', CENTRAL_MINING_STATION_MREA, 0x081d023a, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', CENTRAL_MINING_STATION_MREA, 0x081d023c, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', CENTRAL_MINING_STATION_MREA, 0x081d0247, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
   
#Caretaker Class Drone - Bunch Of Actors

def Enemy_Gun_Turret_Base(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.attack_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.hurt_sleep_delay /= Rand_Speed
    Enemy_props.gun_aim_turn_speed *= Rand_Speed
    Enemy_props.unknown_0x95e7a2c2 /= Rand_Speed # Min of range for random delay before charging gun
    Enemy_props.unknown_0x76ba1c18 /= Rand_Speed # Max of range for random delay before charging gun
    Enemy_props.unknown_0x3eb2de35 /= Rand_Speed # Min of range for random delay between each individual shot
    Enemy_props.unknown_0xe50d8dd2 /= Rand_Speed # Max of range for random delay between each individual shot
    Enemy_props.patrol_delay /= Rand_Speed
    Enemy_props.withdraw_delay /= Rand_Speed
    Enemy_props.attack_delay /= Rand_Speed
    Enemy_props.attack_leash_time /= Rand_Speed
    Enemy.set_properties(Enemy_props)

def Enemy_Gun_Turret_Top(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.power_up_time /= Rand_Speed
    Enemy_props.power_down_time /= Rand_Speed
    COLOR(Enemy_props.light_color, Enemy.id, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Elite_Pirate(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Data_Range["SC_Low"] = 1.0 #Lag spikes sometimes when different scaleing.
    Data_Range["SC_High"] = 1.0
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.melee_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.taunt_interval /= Rand_Speed
    Enemy_props.taunt_variance /= Rand_Speed
    SHOCK_WAVE_INFO(Enemy_props.single_shock_wave_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    SHOCK_WAVE_INFO(Enemy_props.double_shock_wave_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.rocket_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.energy_absorb_duration /= Rand_Speed
    ING_POSSESSION_DATA(Enemy_props.ing_possession_data, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Stone_Toad(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Wall_Walker(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.leg_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.floor_turn_speed *= Rand_Speed
    DAMAGE_INFO(Enemy_props.explode_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.projectile_interval /= Rand_Speed
    DAMAGE_INFO(Enemy_props.projectile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Splitter_Command_Module(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_struct43.max_linear_velocity *= Rand_Speed
    Enemy_props.unknown_struct43.max_turn_speed *= Rand_Speed
    Enemy_props.unknown_struct43.scanning_turn_speed *= Rand_Speed
    Enemy_props.unknown_struct43.unknown_0xe32fcae9 /= Rand_Speed #Delay to shoot after it stops dashing
    DAMAGE_INFO(Enemy_props.unknown_struct43.laser_pulse_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_struct43.reset_shield_time /= Rand_Speed
    Enemy_props.unknown_struct43.split_destroyed_priority *= Rand_Health # Variable name is incorrect, its the heatlh of the shield when the head is detached
    Enemy_props.unknown_struct43.laser_sweep_turn_speed *= Rand_Speed
    DAMAGE_INFO(Enemy_props.unknown_struct43.laser_sweep_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PLASMA_BEAM_INFO(Enemy_props.unknown_struct43.laser_sweep_beam_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    COLOR(Enemy_props.unknown_struct43.unknown_struct42.cloud_color1, Enemy.id, rng)
    COLOR(Enemy_props.unknown_struct43.unknown_struct42.cloud_color2, Enemy.id, rng)
    COLOR(Enemy_props.unknown_struct43.unknown_struct42.add_color1, Enemy.id, rng)
    COLOR(Enemy_props.unknown_struct43.unknown_struct42.add_color2, Enemy.id, rng)
    Enemy_props.unknown_struct43.unknown_struct42.cloud_scale *= (Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3
    Enemy_props.unknown_struct43.unknown_struct42.fade_off_size *= (Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3
    Enemy_props.unknown_struct43.unknown_struct42.open_speed *= Rand_Speed
    ING_POSSESSION_DATA(Enemy_props.unknown_struct43.ing_possession_data, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.unknown_struct43.light_shield_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.unknown_struct43.dark_shield_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Splitter_Main_Chassis(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] > 2.0:
        Data_Range["SC_Low"] = 2.0
    if Data_Range["SC_High"] > 2.0:
        Data_Range["SC_High"] = 2.0
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.splitter_main_chassis_data.leg_stab_attack_interval /= Rand_Speed
    #Enemy_props.splitter_main_chassis_data.unknown_0xf6047d40 - Idk, changing this from 2.5 to 10.0 caused his 'leg_stab' to turn into a stomp that doesn't hurt?
    #Enemy_props.splitter_main_chassis_data.unknown_0x5130fd39 - This is the distance before Quad starts 'leg_stab'ing you
    DAMAGE_INFO(Enemy_props.splitter_main_chassis_data.leg_stab_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.splitter_main_chassis_data.min_dodge_interval /= Rand_Speed
    Enemy_props.splitter_main_chassis_data.deployment_speed *= Rand_Speed
    Enemy_props.splitter_main_chassis_data.scan_duration /= Rand_Speed
    Enemy_props.splitter_main_chassis_data.laser_sweep_interval /= Rand_Speed
    Enemy_props.splitter_main_chassis_data.unknown_0x35eedd1c *= Rand_Speed # Speed of spin attack
    Enemy_props.splitter_main_chassis_data.spin_attack_interval /= Rand_Speed
    Enemy_props.splitter_main_chassis_data.unknown_0x43722555 /= Rand_Speed # Delay to move toward you right after getting into spinning mode
    Enemy_props.splitter_main_chassis_data.unknown_0x21296bdc /= Rand_Speed # time spent in spinning mode
    DAMAGE_INFO(Enemy_props.splitter_main_chassis_data.spin_attack_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_POSSESSION_DATA(Enemy_props.splitter_main_chassis_data.ing_possession_data, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.splitter_main_chassis_data.spin_attack_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Bacteria_Swarm(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    BASIC_SWARM_PROPERTIES(Enemy_props.basic_swarm_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.bacteria_patrol_speed *= Rand_Speed
    Enemy_props.bacteria_acceleration *= Rand_Speed
    Enemy_props.bacteria_deceleration *= Rand_Speed
    Enemy_props.patrol_turn_speed *= Rand_Speed
    COLOR(Enemy_props.bacteria_patrol_color, Enemy.id, rng)
    COLOR(Enemy_props.bacteria_player_pursuit_color, Enemy.id, rng)
    Enemy_props.color_change_time /= Rand_Speed
    Enemy.set_properties(Enemy_props)

def Enemy_Minor_Ing(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.projectile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.unknown_struct33.damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_struct33.bomb_stun_duration /= Rand_Speed
    Enemy_props.unknown_struct33.max_speed *= Rand_Speed
    Enemy_props.unknown_struct33.max_wall_speed *= Rand_Speed
    Enemy_props.unknown_struct33.ball_pursuit_speed *= Rand_Speed
    Enemy_props.unknown_struct33.speed_modifier *= Rand_Speed
    Enemy_props.unknown_struct33.turn_speed *= Rand_Speed
    #Enemy_props.unknown_struct33.hit_normal_damage *= Rand_Damage
    #Enemy_props.unknown_struct33.hit_heavy_damage *= Rand_Damage
    DAMAGE_VULNERABILITY(Enemy_props.unknown_struct33.vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    HEALTH(Enemy_props.unknown_struct34.health, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.unknown_struct34.damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_struct34.min_launch_speed *= Rand_Speed
    Enemy_props.unknown_struct34.max_launch_speed *= Rand_Speed
    #Enemy_props.unknown_struct34.min_generation
    #Enemy_props.unknown_struct34.max_generation
    Enemy.set_properties(Enemy_props)

def Enemy_Ing(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.ing_spot_max_speed *= Rand_Speed
    Enemy_props.unknown_0x50398a06 *= Rand_Speed # Speed in puddle form when shot at least once
    Enemy_props.ing_spot_turn_speed *= Rand_Speed
    #Enemy_props.ing_spot_hit_normal_damage *= Rand_Damage
    #Enemy_props.ing_spot_hit_heavy_damage *= Rand_Damage
    Enemy_props.unknown_0xc620183a /= Rand_Speed # delay to start attacking after coming out of puddle
    Enemy_props.frustration_time /= Rand_Speed
    DAMAGE_INFO(Enemy_props.arm_swipe_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.body_projectile_contact_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.body_projectile_suck_time /= Rand_Speed
    Enemy_props.body_projectile_speed *= Rand_Speed
    Enemy_props.body_projectile_drop_time /= Rand_Speed
    DAMAGE_INFO(Enemy_props.mini_portal_projectile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PLASMA_BEAM_INFO(Enemy_props.mini_portal_beam_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.exit_grapple_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.exit_grapple_spit_force
    COLOR(Enemy_props.light_color, Enemy.id, rng)
    DAMAGE_VULNERABILITY(Enemy_props.ing_spot_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.grapple_ball_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.trigger_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Ing_Blob_Swarm(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    BASIC_SWARM_PROPERTIES(Enemy_props.basic_swarm_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.into_attack_speed *= Rand_Speed
    Enemy_props.attack_speed *= Rand_Speed
    Enemy.set_properties(Enemy_props)

def Enemy_Wisp_Tentacle(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    #EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.attack_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.hurt_sleep_delay /= Rand_Speed
    Enemy_props.grab_blend_time /= Rand_Speed
    Enemy.set_properties(Enemy_props)

def Enemy_Medium_Ing(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Rand_Scale['y'] = Rand_Scale['x']
    Rand_Scale['z'] = Rand_Scale['x']
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.min_melee_attack_interval /= Rand_Speed
    DAMAGE_INFO(Enemy_props.melee_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.mist_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.min_mist_attack_interval /= Rand_Speed
    DAMAGE_VULNERABILITY(Enemy_props.misting_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.min_arm_attack_interval /= Rand_Speed
    Enemy_props.arm_attack_time /= Rand_Speed
    Enemy_props.unknown_0x8f1d597c /= Rand_Speed #delay between each tentacle shot in arm attack
    DAMAGE_INFO(Enemy_props.attack_tentacle_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    COLOR(Enemy_props.light_color, Enemy.id, rng)
    #print(Enemy_props.dash_speed) - spline
    Enemy.set_properties(Enemy_props)

def Enemy_Digital_Guardian(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] < 0.01:
        Data_Range["SC_Low"] = 0.01
    if Data_Range["SC_High"] > 4.0:
        Data_Range["SC_High"] = 4.0
    if Data_Range["SC_Low"] > Data_Range["SC_High"]:
        Data_Range["SC_Low"] = Data_Range["SC_High"]
    if Data_Range["SC_High"] < Data_Range["SC_Low"]:
        Data_Range["SC_High"] = Data_Range["SC_Low"]
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.digital_guardian_data.leg_stab_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    SHOCK_WAVE_INFO(Enemy_props.digital_guardian_data.shock_wave_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.digital_guardian_data.vortex_attack_duration /= Rand_Speed
    #Enemy_props.digital_guardian_data.vortex_attraction_force
    Enemy_props.digital_guardian_data.vortex_linear_velocity *= Rand_Speed
    Enemy_props.digital_guardian_data.vortex_linear_acceleration *= Rand_Speed
    #Enemy_props.digital_guardian_data.unknown_0x1cc6d870 /= Rand_Speed - Time spent doing nothing right after cutscene of body and head discconecting (2nd cutscene, not 3rd)
    DAMAGE_INFO(Enemy_props.digital_guardian_data.vortex_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.digital_guardian_data.jump_timer /= Rand_Speed
    Enemy_props.digital_guardian_data.unknown_0x8106cda9 *= Rand_Speed #Default Movement Speed
    Enemy_props.digital_guardian_data.unknown_0x9e1b8105 *= Rand_Speed #Movement Speed after 1 kneecap destroyed
    Enemy_props.digital_guardian_data.unknown_0xa08fcc70 *= Rand_Speed #Movement Speed after 2 kneecaps destroyed
    Enemy_props.digital_guardian_data.unknown_0x3254a16b *= Rand_Speed #Movement Speed after 3 kneecaps destroyed
    Enemy_props.digital_guardian_data.unknown_0xe3dd61e6 *= Rand_Health #Kneecap Health
    Enemy_props.digital_guardian_data.unknown_0x4f6d27d3 *= Rand_Health #Antenna Health
    DAMAGE_VULNERABILITY(Enemy_props.digital_guardian_data.knee_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.digital_guardian_data.vortex_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.digital_guardian_data.toe_target_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)
    if Enemy.id == 0x2c350060:
        TEMP(editor, 'SEQUENCE_TIMER', HIVE_TEMPLE_MREA, 0x2c350323, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'SEQUENCE_TIMER', HIVE_TEMPLE_MREA, 0x2c3502da, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)

def Enemy_Digital_Guardian_Head(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] < 0.05:
        Data_Range["SC_Low"] = 0.05
    if Data_Range["SC_High"] > 1.4:
        Data_Range["SC_High"] = 1.4
    if Data_Range["SC_Low"] > Data_Range["SC_High"]:
        Data_Range["SC_Low"] = Data_Range["SC_High"]
    if Data_Range["SC_High"] < Data_Range["SC_Low"]:
        Data_Range["SC_High"] = Data_Range["SC_Low"]
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.digital_guardian_head_data.max_turn_speed *= Rand_Speed
    Enemy_props.digital_guardian_head_data.max_linear_velocity *= Rand_Speed
    Enemy_props.digital_guardian_head_data.unknown_0xe7de8b82 *= Rand_Health #3rd phase yellow health
    #Enemy_props.digital_guardian_head_data.unknown_0x12ebb390 *= int(Rand_Health) #2nd phase head anetenna health
    PLASMA_BEAM_INFO(Enemy_props.digital_guardian_head_data.plasma_beam_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.digital_guardian_head_data.lock_on_missiles_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.digital_guardian_head_data.machine_gun_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DIGITAL_GUARDIAN_HEAD_STRUCT(Enemy_props.digital_guardian_head_data.digital_guardian_head_struct_0x8f6732ea, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DIGITAL_GUARDIAN_HEAD_STRUCT(Enemy_props.digital_guardian_head_data.digital_guardian_head_struct_0x8e128141, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DIGITAL_GUARDIAN_HEAD_STRUCT(Enemy_props.digital_guardian_head_data.digital_guardian_head_struct_0xea54b390, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DIGITAL_GUARDIAN_HEAD_STRUCT(Enemy_props.digital_guardian_head_data.digital_guardian_head_struct_0xbbd3e7a7, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DIGITAL_GUARDIAN_HEAD_STRUCT(Enemy_props.digital_guardian_head_data.digital_guardian_head_struct_0x2dd88764, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DIGITAL_GUARDIAN_HEAD_STRUCT(Enemy_props.digital_guardian_head_data.digital_guardian_head_struct_0x48b46e55, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.digital_guardian_head_data.bomb_pit_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.digital_guardian_head_data.echo_target_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Ing_Space_Jump_Guardian(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] < 0.01:
        Data_Range["SC_Low"] = 0.01
    if Data_Range["SC_High"] > 2.5:
        Data_Range["SC_High"] = 2.5
    if Data_Range["SC_Low"] > Data_Range["SC_High"]:
        Data_Range["SC_Low"] = Data_Range["SC_High"]
    if Data_Range["SC_High"] < Data_Range["SC_Low"]:
        Data_Range["SC_High"] = Data_Range["SC_Low"]
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_SPACE_JUMP_GUARDIAN_STRUCT(Enemy_props.unknown_struct32.ing_space_jump_guardian_struct_0x5e1d1931, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_SPACE_JUMP_GUARDIAN_STRUCT(Enemy_props.unknown_struct32.ing_space_jump_guardian_struct_0x6b08e2e5, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_SPACE_JUMP_GUARDIAN_STRUCT(Enemy_props.unknown_struct32.ing_space_jump_guardian_struct_0xf223aa76, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_SPACE_JUMP_GUARDIAN_STRUCT(Enemy_props.unknown_struct32.ing_space_jump_guardian_struct_0xd0db5f7a, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    COLOR(Enemy_props.unknown_struct32.light_color, Enemy.id, rng)
    DAMAGE_INFO(Enemy_props.unknown_struct32.mini_portal_projectile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PLASMA_BEAM_INFO(Enemy_props.unknown_struct32.mini_portal_beam_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    SHOCK_WAVE_INFO(Enemy_props.unknown_struct32.shock_wave_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Ing_Boost_Ball_Guardian(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] < 0.05:
        Data_Range["SC_Low"] = 0.05
    if Data_Range["SC_High"] > 1.8:
        Data_Range["SC_High"] = 1.8
    if Data_Range["SC_Low"] > Data_Range["SC_High"]:
        Data_Range["SC_Low"] = Data_Range["SC_High"]
    if Data_Range["SC_High"] < Data_Range["SC_Low"]:
        Data_Range["SC_High"] = Data_Range["SC_Low"]
    if Data_Range["SP_Low"] > 2.0:
        Data_Range["SP_Low"] = 2.0
    if Data_Range["SP_High"] > 2.0:
        Data_Range["SP_High"] = 2.0
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_struct28.ing_spot_max_speed *= Rand_Speed
    Enemy_props.unknown_struct28.unknown_0x50398a06 *= Rand_Speed# Speed in puddle form when shot at least once
    Enemy_props.unknown_struct28.ing_spot_turn_speed *= Rand_Speed
    #Enemy_props.unknown_struct28.ing_spot_hit_normal_damage *= Rand_Damage
    #Enemy_props.unknown_struct28.ing_spot_hit_heavy_damage *= Rand_Damage
    Enemy_props.unknown_struct28.frustration_time /= Rand_Speed
    DAMAGE_INFO(Enemy_props.unknown_struct28.arm_swipe_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.unknown_struct28.body_projectile_contact_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_struct28.body_projectile_suck_time /= Rand_Speed
    Enemy_props.unknown_struct28.body_projectile_speed /= Rand_Speed
    Enemy_props.unknown_struct28.body_projectile_drop_time /= Rand_Speed
    DAMAGE_INFO(Enemy_props.unknown_struct28.mini_portal_projectile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PLASMA_BEAM_INFO(Enemy_props.unknown_struct28.mini_portal_beam_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    COLOR(Enemy_props.unknown_struct28.light_color, Enemy.id, rng)
    DAMAGE_VULNERABILITY(Enemy_props.unknown_struct28.ing_spot_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_struct29.boost_ball_scale.x *= Rand_Scale['x']
    Enemy_props.unknown_struct29.boost_ball_scale.y *= Rand_Scale['y']
    Enemy_props.unknown_struct29.boost_ball_scale.z *= Rand_Scale['z']
    #Enemy_props.unknown_struct29.boost_ball_speed *= Rand_Speed - spline
    DAMAGE_INFO(Enemy_props.unknown_struct29.damage_info_0x0e1a78bd, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.unknown_struct29.damage_info_0x19c3d263, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.unknown_struct29.boost_ball_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.unknown_struct29.damage_info_0x5616d5f1, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.unknown_struct29.damage_info_0xed685533, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_BOOST_BALL_GUARDIAN_STRUCT(Enemy_props.unknown_struct29.ing_boost_ball_guardian_struct_0xbab98497, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_BOOST_BALL_GUARDIAN_STRUCT(Enemy_props.unknown_struct29.ing_boost_ball_guardian_struct_0xfe18a18f, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_BOOST_BALL_GUARDIAN_STRUCT(Enemy_props.unknown_struct29.ing_boost_ball_guardian_struct_0xc2784287, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Ing_Spider_ball_Guardian(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] < 0.05:
        Data_Range["SC_Low"] = 0.05
    if Data_Range["SC_High"] > 1.5:
        Data_Range["SC_High"] = 1.5
    if Data_Range["SC_Low"] > Data_Range["SC_High"]:
        Data_Range["SC_Low"] = Data_Range["SC_High"]
    if Data_Range["SC_High"] < Data_Range["SC_Low"]:
        Data_Range["SC_High"] = Data_Range["SC_Low"]
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Rand_Health = 1.0 # yeaaaa that was a mistake changing his health
    Rand_Scale['y'] = Rand_Scale['x']
    Rand_Scale['z'] = Rand_Scale['x'] # First time I tested him with different XYZ's after the first electric node got him, he went offscreen and... triggered a node in the 3rd section and I couldn't get past the 2nd.
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_SPIDER_BALL_GUARDIAN_STRUCT(Enemy_props.unknown_struct31.ing_spiderball_guardian_struct_0x152db484, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_SPIDER_BALL_GUARDIAN_STRUCT(Enemy_props.unknown_struct31.ing_spiderball_guardian_struct_0x2d163ff7, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_SPIDER_BALL_GUARDIAN_STRUCT(Enemy_props.unknown_struct31.ing_spiderball_guardian_struct_0x8c2fbb19, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_SPIDER_BALL_GUARDIAN_STRUCT(Enemy_props.unknown_struct31.ing_spiderball_guardian_struct_0x5d612911, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_SPIDER_BALL_GUARDIAN_STRUCT(Enemy_props.unknown_struct31.ing_spiderball_guardian_struct_0xfc58adff, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_SPIDER_BALL_GUARDIAN_STRUCT(Enemy_props.unknown_struct31.ing_spiderball_guardian_struct_0xc463268c, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_struct31.damage_radius *= (Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3
    DAMAGE_INFO(Enemy_props.unknown_struct31.proximity_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)
    TRIGGER = [0x34140096, 0x3414009c, 0x34140097, 0x34140099, 0x34140098, 0x3414009e]
    if Enemy.id == 0x3414007a:
        TEMP(editor, 'PLATFORM', DYNAMO_WORKS_MREA, 0x0c1400f7, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'PLATFORM', DYNAMO_WORKS_MREA, 0x28140404, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        for i in TRIGGER:
            Temp = (editor.get_mrea(DYNAMO_WORKS_MREA)).get_instance(i)
            Temp_props: Temp = Temp.get_properties()
            if Temp.name == 'Electric Coil 1 Damage' or Temp.name == 'Electric Coil 4 Damage' or Temp.name == 'Electric Coil 5 Damage' or Temp.name == 'Electric Coil 6 Damage':
                Temp_props.editor_properties.transform.scale.x = 5.0 # If Spider Guardian is to small he can sneak past the electric coil triggers so this stops that
            else:
                Temp_props.editor_properties.transform.scale.y = 5.0
            Temp.set_properties(Temp_props)

def Enemy_Sand_Boss(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] < 0.4:
        Data_Range["SC_Low"] = 0.4
    if Data_Range["SC_High"] > 1.78:
        Data_Range["SC_High"] = 1.78
    if Data_Range["SC_Low"] > Data_Range["SC_High"]:
        Data_Range["SC_Low"] = Data_Range["SC_High"]
    if Data_Range["SC_High"] < Data_Range["SC_Low"]:
        Data_Range["SC_High"] = Data_Range["SC_Low"]
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.sand_boss_data.snap_jaw_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.sand_boss_data.spit_out_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.sand_boss_data.unknown_0xbf88fe4f /= Rand_Speed #Max Random delay for attacking
    Enemy_props.sand_boss_data.unknown_0x74c702b3 /= Rand_Speed #Min Random delay for attacking
    DAMAGE_INFO(Enemy_props.sand_boss_data.dark_beam_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.sand_boss_data.unknown_0xd0db2574 *= Rand_Health # Helmet health
    #Enemy_props.sand_boss_data.suck_air_time /= Rand_Speed
    #Enemy_props.sand_boss_data.spit_morphball_time /= Rand_Speed
    DAMAGE_INFO(Enemy_props.sand_boss_data.unknown_struct40.damage_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.sand_boss_data.unknown_struct41.sand_boss_struct_b_0xb9784f0e.damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.sand_boss_data.unknown_struct41.sand_boss_struct_b_0xb9784f0e.duration /= Rand_Speed
    Enemy_props.sand_boss_data.unknown_struct41.sand_boss_struct_b_0xb9784f0e.change_direction_interval /= Rand_Speed
    Enemy_props.sand_boss_data.unknown_struct41.sand_boss_struct_b_0xb9784f0e.turn_speed *= Rand_Speed
    DAMAGE_INFO(Enemy_props.sand_boss_data.unknown_struct41.sand_boss_struct_b_0xb8ae1bdc.damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.sand_boss_data.unknown_struct41.sand_boss_struct_b_0xb8ae1bdc.duration /= Rand_Speed
    Enemy_props.sand_boss_data.unknown_struct41.sand_boss_struct_b_0xb8ae1bdc.change_direction_interval /= Rand_Speed
    Enemy_props.sand_boss_data.unknown_struct41.sand_boss_struct_b_0xb8ae1bdc.turn_speed *= Rand_Speed
    PLASMA_BEAM_INFO(Enemy_props.sand_boss_data.unknown_struct41.charge_beam_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.sand_boss_data.damage_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.sand_boss_data.stampede_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.sand_boss_data.suck_air_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)
    #print(Enemy_props.editor_properties.transform.scale)
    Temp = (editor.get_mrea(DARK_AGON_TEMPLE_MREA)).get_instance(0x14240007)
    Temp_props: temp = Temp.get_properties()
    if Temp_props.editor_properties.transform.scale.x > Rand_Scale['x']:
        Temp_props.editor_properties.transform.scale.x = Rand_Scale['x']
    if Temp_props.editor_properties.transform.scale.y > Rand_Scale['y']:
        Temp_props.editor_properties.transform.scale.y = Rand_Scale['y']
    if Temp_props.editor_properties.transform.scale.z > Rand_Scale['z']:
        Temp_props.editor_properties.transform.scale.z = Rand_Scale['z']
    Temp.set_properties(Temp_props)
    
    if Enemy.id == 0x14240008:
        TEMP(editor, 'ACTOR', DARK_AGON_TEMPLE_MREA, 0x202401b7, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', DARK_AGON_TEMPLE_MREA, 0x4024034e, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', DARK_AGON_TEMPLE_MREA, 0x24240279, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', DARK_AGON_TEMPLE_MREA, 0x24240229, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', DARK_AGON_TEMPLE_MREA, 0x24240258, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', DARK_AGON_TEMPLE_MREA, 0x24240223, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', DARK_AGON_TEMPLE_MREA, 0x24240233, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', DARK_AGON_TEMPLE_MREA, 0x2424026f, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', DARK_AGON_TEMPLE_MREA, 0x24240225, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', DARK_AGON_TEMPLE_MREA, 0x24240239, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    elif Enemy.id == 0x14240009:
        TEMP(editor, 'ACTOR', DARK_AGON_TEMPLE_MREA, 0x202401c1, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', DARK_AGON_TEMPLE_MREA, 0x20240194, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    elif Enemy.id == 0x14240006:
        TEMP(editor, 'ACTOR', DARK_AGON_TEMPLE_MREA, 0x20240197, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', DARK_AGON_TEMPLE_MREA, 0x202401bf, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)

def Enemy_Swamp_Boss_Stage_1(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] < 0.05:
        Data_Range["SC_Low"] = 0.05
    if Data_Range["SC_High"] > 1.5:
        Data_Range["SC_High"] = 1.5
    if Data_Range["SC_Low"] > Data_Range["SC_High"]:
        Data_Range["SC_Low"] = Data_Range["SC_High"]
    if Data_Range["SC_High"] < Data_Range["SC_Low"]:
        Data_Range["SC_High"] = Data_Range["SC_Low"]
    if Data_Range["SP_Low"] > 2.0:
        Data_Range["SP_Low"] = 2.0
    if Data_Range["SP_High"] > 2.0:
        Data_Range["SP_High"] = 2.0
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_struct37.unknown_0x27a06f6a /= Rand_Speed #Min-range for delay to bob up then down (when swimming around the platform in a circle)
    Enemy_props.unknown_struct37.unknown_0x233a5e40 /= Rand_Speed #Man-range for delay to bob up then down (when swimming around the platform in a circle)
    SHOCK_WAVE_INFO(Enemy_props.unknown_struct37.splash_shock_wave, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.unknown_struct37.damage_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.unknown_struct37.weak_spot_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_struct37.weak_spot_damage_multiplier *= Rand_Damage
    DAMAGE_INFO(Enemy_props.unknown_struct37.spit_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_struct37.swamp_boss_stage1_struct_0x4500f774.unknown_0x98106ee2 *= Rand_Health
    Enemy_props.unknown_struct37.swamp_boss_stage1_struct_0x4500f774.unknown_0x95e7a2c2 /= Rand_Speed #Min-range for delay to go underwater (from swimming in circle)
    Enemy_props.unknown_struct37.swamp_boss_stage1_struct_0x4500f774.unknown_0x76ba1c18 /= Rand_Speed #Man-range for delay to go underwater (from swimming in circle)
    Enemy_props.unknown_struct37.swamp_boss_stage1_struct_0x3e1e7597.unknown_0x98106ee2 *= Rand_Health
    Enemy_props.unknown_struct37.swamp_boss_stage1_struct_0x3e1e7597.unknown_0x95e7a2c2 /= Rand_Speed #Min-range for delay to go underwater (from swimming in circle)
    Enemy_props.unknown_struct37.swamp_boss_stage1_struct_0x3e1e7597.unknown_0x76ba1c18 /= Rand_Speed #Man-range for delay to go underwater (from swimming in circle)
    Enemy.set_properties(Enemy_props)
    if Enemy.id == 0x0c2001c1:
        TEMP(editor, 'ACTOR', DARK_TORVUS_TEMPLE_MREA, 0x1020038e, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', DARK_TORVUS_TEMPLE_MREA, 0x3020047c, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)

def Enemy_Swamp_Boss_Stage_2(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] < 0.05:
        Data_Range["SC_Low"] = 0.05
    if Data_Range["SC_High"] > 2.5:
        Data_Range["SC_High"] = 2.5
    if Data_Range["SC_Low"] > Data_Range["SC_High"]:
        Data_Range["SC_Low"] = Data_Range["SC_High"]
    if Data_Range["SC_High"] < Data_Range["SC_Low"]:
        Data_Range["SC_High"] = Data_Range["SC_Low"]
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Rand_Scale['y'] = Rand_Scale['x']
    Rand_Scale['z'] = Rand_Scale['x']
    Rand_Speed = float("{0:.1f}".format(Rand_Speed)) #Adult chykka can have a seizure if it has to many decimal points
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_POSSESSION_DATA(Enemy_props.ing_possession_data, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.swamp_boss_stage2_data.hover_speed *= Rand_Speed
    SWAMP_BOSS_STAGE2_STRUCT(Enemy_props.swamp_boss_stage2_data.swamp_boss_stage2_struct_0x7fa9256a, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    SWAMP_BOSS_STAGE2_STRUCT(Enemy_props.swamp_boss_stage2_data.swamp_boss_stage2_struct_0x8b884b8e, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    SWAMP_BOSS_STAGE2_STRUCT(Enemy_props.swamp_boss_stage2_data.swamp_boss_stage2_struct_0x04b7a789, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    SWAMP_BOSS_STAGE2_STRUCT(Enemy_props.swamp_boss_stage2_data.swamp_boss_stage2_struct_0xf096c96d, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    #Enemy_props.swamp_boss_stage2_data.stun_time /= Rand_Speed
    DAMAGE_INFO(Enemy_props.swamp_boss_stage2_data.spit_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.swamp_boss_stage2_data.swoop_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.swamp_boss_stage2_data.swoop_damage_time *= Rand_Speed
    SHOCK_WAVE_INFO(Enemy_props.swamp_boss_stage2_data.splash_shock_wave, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    #Enemy_props.swamp_boss_stage2_data.unknown_struct38.turn_rate /= Rand_Speed
    Enemy_props.swamp_boss_stage2_data.unknown_struct38.warp_scale *= (Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3
    DAMAGE_INFO(Enemy_props.swamp_boss_stage2_data.blow_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.swamp_boss_stage2_data.break_stun_damage *= Rand_Damage
    Enemy_props.swamp_boss_stage2_data.unknown_0x8fe0bf01 /= Rand_Speed #Attack delay of Dark Chykka (excluding first attack)
    Enemy_props.swamp_boss_stage2_data.unknown_0x19849710 /= Rand_Speed #Attack Delay?
    Enemy.set_properties(Enemy_props)
    if Enemy.id == 0x182002ca:
        TEMP(editor, 'ACTOR', DARK_TORVUS_TEMPLE_MREA, 0x1c2003c0, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)

def Enemy_Emperor_Ing_Stage_1(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] < 0.05:
        Data_Range["SC_Low"] = 0.05
    if Data_Range["SC_High"] > 1.3:
        Data_Range["SC_High"] = 1.3
    if Data_Range["SC_Low"] > Data_Range["SC_High"]:
        Data_Range["SC_Low"] = Data_Range["SC_High"]
    if Data_Range["SC_High"] < Data_Range["SC_Low"]:
        Data_Range["SC_High"] = Data_Range["SC_Low"]
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    HEALTH(Enemy_props.data.tentacle.health, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.data.tentacle.normal_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.data.tentacle.warp_attack_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.data.tentacle.melee_attack_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.data.tentacle.projectile_attack_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.data.tentacle.stay_retracted_time /= Rand_Speed
    DAMAGE_INFO(Enemy_props.data.unknown_struct20.damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.data.unknown_struct21.projectile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.data.unknown_struct22.stab_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.data.unknown_struct23.loop_duration /= Rand_Speed
    SHOCK_WAVE_INFO(Enemy_props.data.unknown_struct23.shock_wave_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PLASMA_BEAM_INFO(Enemy_props.data.unknown_struct24.beam_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.data.unknown_struct24.damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    #Enemy_props.data.heart_exposed_time /= Rand_Speed - no
    Enemy_props.data.unknown_0xb826317a *= Rand_Speed #Speed of something
    Enemy_props.data.turn_speed_accel *= Rand_Speed
    Enemy_props.data.max_turn_speed_normal *= Rand_Speed
    Enemy_props.data.max_turn_speed_melee *= Rand_Speed
    Enemy_props.data.unknown_0xe5a7c358 *= Rand_Speed #Speed of something
    #Enemy_props.data.taunt_frequency /= Rand_Speed
    Enemy_props.data.attack_interval_min /= Rand_Speed
    Enemy_props.data.attack_interval_max /= Rand_Speed
    Enemy.set_properties(Enemy_props)

    ACTORKEYFRAME = [0x1c0b0078, 0x080b00dc, 0x080b00e0]
    ACTORROTATE = [0x080b00e3, 0x080b00e7, 0x080b00e3]
    ACTOR = [0x080b0015, 0x080b0016, 0x080b008c, 0x140b000e, 0x140b0273, 0x140b0255, 0x140b0262, 0x140b02d3, 0x140b0267, 0x140b026c, 0x180b01d4, 0x180b01d5]
    PLATFORM = [0x080b001a, 0x180b01dc, 0x1c0b006d] 
    EFFECT = [0x140b0010, 0x140b0270, 0x140b027a, 0x200b01e4, 0x200b020d, 0x140b0266, 0x080b0096, 0x180b01c4, 0x0c0b00b5, 0x0c0b00b6, 0x0c0b00b7, 0x0c0b00b8,
              0x0c0b00ba, 0x0c0b00cf, 0x0c0b00d0, 0x0c0b00d1, 0x0c0b00d2, 0x0c0b00d3 , 0x0c0b00d4, 0x1c0b02ec, 0x1c0b02ee, 0x1c0b02f0, 0x200b020d, 0x200b01f1,
              0x200b022d, 0x200b001c, 0x200b01fc]
    for i in ACTORKEYFRAME:
        TEMP(editor, 'ACTOR_KEY_FRAME', SANCTUM_MREA, i, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    for i in ACTORROTATE:
        TEMP(editor, 'ACTOR_ROTATE', SANCTUM_MREA, i, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    for i in ACTOR:
        TEMP(editor, 'ACTOR', SANCTUM_MREA, i, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    for i in PLATFORM:
        if i == 0x080b001a:
            Temp = (editor.get_mrea(SANCTUM_MREA)).get_instance(i)
            Temp_props: Temp = Temp.get_properties()
            Temp_props.collision_model = 0
            Temp.set_properties(Temp_props)
        else:
            TEMP(editor, 'PLATFORM', SANCTUM_MREA, i, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    for i in EFFECT:
        TEMP(editor, 'EFFECT', SANCTUM_MREA, i, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    Temp = (editor.get_mrea(SANCTUM_MREA)).get_instance(0x080b0131)
    Temp_props: Temp = Temp.get_properties()
    EDITOR_PROPERTIES(Temp_props.editor_properties, None, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Temp.set_properties(Temp_props)
    

def Enemy_Emperor_Ing_Stage_2(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] < 0.2:
        Data_Range["SC_Low"] = 0.2
    if Data_Range["SC_High"] > 3.0:
        Data_Range["SC_High"] = 3.0
    if Data_Range["SC_Low"] > Data_Range["SC_High"]:
        Data_Range["SC_Low"] = Data_Range["SC_High"]
    if Data_Range["SC_High"] < Data_Range["SC_Low"]:
        Data_Range["SC_High"] = Data_Range["SC_Low"]
    if Data_Range["SP_Low"] < 0.25:
        Data_Range["SP_Low"] = 0.25
    if Data_Range["SP_High"] < 0.25:
        Data_Range["SP_High"] = 0.25
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.data.detection_time /= Rand_Speed
    Enemy_props.data.forget_time /= Rand_Speed
    Enemy.set_properties(Enemy_props)
    
def Enemy_Emperor_Ing_Stage_3(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] < 0.1:
        Data_Range["SC_Low"] = 0.1
    if Data_Range["SC_High"] > 1.5:
        Data_Range["SC_High"] = 1.5
    if Data_Range["SC_Low"] > Data_Range["SC_High"]:
        Data_Range["SC_Low"] = Data_Range["SC_High"]
    if Data_Range["SC_High"] < Data_Range["SC_Low"]:
        Data_Range["SC_High"] = Data_Range["SC_Low"]
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    #Enemy_props.data.taunt_frequency /= Rand_Speed
    HEALTH(Enemy_props.data.yellow_health, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    HEALTH(Enemy_props.data.health, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.data.vulnerable_time /= Rand_Speed
    DAMAGE_VULNERABILITY(Enemy_props.data.red_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.data.light_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.data.dark_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.data.melee_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.data.damage_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.data.jump_slide_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.data.ground_pound_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    BASIC_SWARM_PROPERTIES(Enemy_props.data.light_swarm_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.data.unknown_struct26.projectile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PLASMA_BEAM_INFO(Enemy_props.data.unknown_struct26.beam_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    SHOCK_WAVE_INFO(Enemy_props.data.jump_attack_shock_wave_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    EMPEROR_ING_STAGE3_STRUCT_B(Enemy_props.data.emperor_ing_stage3_struct_b_0xe843417f, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    EMPEROR_ING_STAGE3_STRUCT_B(Enemy_props.data.emperor_ing_stage3_struct_b_0xd13bec3f, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    EMPEROR_ING_STAGE3_STRUCT_B(Enemy_props.data.emperor_ing_stage3_struct_b_0xc61388ff, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    EMPEROR_ING_STAGE3_STRUCT_B(Enemy_props.data.emperor_ing_stage3_struct_b_0xa3cab6bf, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

    ACTOR = [0x000b0077, 0x200b0221, 0x200b0223]
    EFFECT = [0x200b0235, 0x200b01f0]

    for i in ACTOR:
        TEMP(editor, 'ACTOR', SANCTUM_MREA, i, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    for i in EFFECT:
        TEMP(editor, 'EFFECT', SANCTUM_MREA, i, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    
def Enemy_Puddle_Spore(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.charge_time /= Rand_Speed
    Enemy_props.time_open /= Rand_Speed
    Enemy_props.platform_time /= Rand_Speed
    SHOCK_WAVE_INFO(Enemy_props.shock_wave_info, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Dark_Commando(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.dark_commando_properties.blade_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.dark_commando_properties.unknown_struct12.grenade_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.dark_commando_properties.unknown_struct13.damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.dark_commando_properties.unknown_struct13.mold_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.dark_commando_properties.unknown_struct14.shadow_dash_speed *= Rand_Speed
    DAMAGE_VULNERABILITY(Enemy_props.dark_commando_properties.unknown_struct14.shadow_decoy_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.dark_commando_properties.unknown_struct14.shadow_dash_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Dark_Trooper(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_POSSESSION_DATA(Enemy_props.ing_possession_data, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.melee_attack_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown /= Rand_Speed #time until they starts shooting (only for the first attack...)
    DAMAGE_INFO(Enemy_props.ranged_attack_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.missile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Puffer(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.hover_speed *= Rand_Speed
    DAMAGE_INFO(Enemy_props.cloud_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.explosion_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Space_Pirate(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    if Enemy.id in [0x081D000F, 0x081b020e, 0x081b0209, 0x081b0202, 0x081b01f8]:
        return
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_POSSESSION_DATA(Enemy_props.ing_possession_data, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.projectile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.blade_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.kneel_attack_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_0x71587b45 /= Rand_Speed #Min of range for delay between shots
    Enemy_props.unknown_0x7903312e /= Rand_Speed #Max of range for delay between shots
    Enemy_props.gun_track_delay /= Rand_Speed
    #weapon_data
    Enemy.set_properties(Enemy_props)

def Enemy_Commando_Pirate(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Enemy.id in [0x08180082, 0x0818001e]:
        Data_Range["SC_Low"] = 1.0
        Data_Range["SC_High"] = 1.0
        if Data_Range["SP_Low"] < 0.05:
            Data_Range["SP_Low"] = 0.05
        if Data_Range["SP_High"] < 2.0:
            Data_Range["SP_High"] = 2.0
        if Data_Range["SP_Low"] > Data_Range["SP_High"]:
            Data_Range["SP_Low"] = Data_Range["SP_High"]
        if Data_Range["SP_High"] < Data_Range["SP_Low"]:
            Data_Range["SP_High"] = Data_Range["SP_Low"]
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    ING_POSSESSION_DATA(Enemy_props.ing_possession_data, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.blade_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.projectile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_struct10.grenade_min_attack_interval /= Rand_Speed
    DAMAGE_INFO(Enemy_props.unknown_struct10.grenade_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.unknown_struct11.shield_charge_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.unknown_struct11.shield_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.unknown_struct11.shield_charge_speed *= Rand_Speed
    Enemy_props.unknown_struct11.arm_shield_time /= Rand_Speed
    Enemy.set_properties(Enemy_props)

def Enemy_Flying_Pirate(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.projectile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.missile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.hurl_recover_time /= Rand_Speed
    #Enemy_props.hover_height
    DAMAGE_INFO(Enemy_props.rocket_pack_explosion_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.minimum_missile_time /= Rand_Speed
    Enemy.set_properties(Enemy_props)

def Enemy_Metroid_Alpha(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.frozen_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.energy_drain_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(Enemy_props.damage_vulnerability, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy_props.telegraph_attack_time /= Rand_Speed
    Enemy_props.baby_metroid_scale /= (Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3
    Enemy_props.unknown_0x2fe164c4 *= (Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3 # Scale after it grows
    Enemy_props.unknown_0x4c1f78f3 *= Rand_Health # once this health value is reached, it grows
    Enemy_props.unknown_0x5f3f294c *= Rand_Health # Metroid Health
    ING_POSSESSION_DATA(Enemy_props.ing_possession_data, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)

def Enemy_Dark_Samus(Enemy: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    if Data_Range["SC_Low"] < 0.05:
        Data_Range["SC_Low"] = 0.05
    if Data_Range["SC_High"] > 3.0:
        Data_Range["SC_High"] = 3.0
    if Data_Range["SC_Low"] > Data_Range["SC_High"]:
        Data_Range["SC_Low"] = Data_Range["SC_High"]
    if Data_Range["SC_High"] < Data_Range["SC_Low"]:
        Data_Range["SC_High"] = Data_Range["SC_Low"]
    if Data_Range["SP_Low"] > 2.0:
        Data_Range["SP_Low"] = 2.0
    if Data_Range["SP_High"] > 2.0:
        Data_Range["SP_High"] = 2.0
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Enemy_props: Enemy = Enemy.get_properties()
    EDITOR_PROPERTIES(Enemy_props.editor_properties, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    PATTERNED(Enemy_props.patterned, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.melee_attack_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.dive_attack_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.scatter_shot_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.normal_missile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.super_missile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.freeze_beam_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.sweep_beam_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.boost_ball_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.damage_info_0x18402aa9, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.damage_info_0x58769eb2, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.phazon_projectile_damage, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_INFO(Enemy_props.damage_info_0x8f3af226, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Enemy.set_properties(Enemy_props)
    #The following changes the size/speed of corrosponding Actors/DarkSamusBattleStages
    if Enemy.id == 0x182e00c4:
        TEMP(editor, 'UNKNOWN_STRUCT17', MAIN_REACTOR_MREA, 0x182e0198, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'UNKNOWN_STRUCT17', MAIN_REACTOR_MREA, 0x182e019f, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'UNKNOWN_STRUCT17', MAIN_REACTOR_MREA, 0x182e009e, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', SECURITY_STATION_B_MREA, 0x083100a4, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', SECURITY_STATION_B_MREA, 0x0831009f, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    elif Enemy.id == 0x083d0054:
        
        TEMP(editor, 'UNKNOWN_STRUCT17', AERIE_ACCESS_MREA, 0x083d0043, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', TRAINING_CHAMBER_MREA, 0x1837018b, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'ACTOR', SANCTUARY_ENTRANCE_MREA, 0x08020277, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    elif Enemy.id == 0x0841012d:
        TEMP(editor, 'UNKNOWN_STRUCT17', AERIE_MREA, 0x08410173, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'UNKNOWN_STRUCT17', AERIE_MREA, 0x08410172, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'UNKNOWN_STRUCT17', AERIE_MREA, 0x08410175, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'UNKNOWN_STRUCT17', AERIE_MREA, 0x08410176, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'UNKNOWN_STRUCT17', AERIE_MREA, 0x08410177, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'UNKNOWN_STRUCT17', AERIE_MREA, 0x08410174, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    elif Enemy.id == 0x102a0001:
        TEMP(editor, 'PLATFORM', SKY_TEMPLE_GATEWAY_MREA, 0x102a0044, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
        TEMP(editor, 'PLATFORM', SKY_TEMPLE_GATEWAY_MREA, 0x102a0045, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)

def Other_Color_Modulate(Other: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Other_props: Other = Other.get_properties()
    COLOR(Other_props.color_a, Other.id, rng)
    COLOR(Other_props.color_b, Other.id, rng)
    Other.set_properties(Other_props)

def Other_Generator(Other: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale = Randomize_Values(rng, Data_Range)[0]
    Other_props: Other = Other.get_properties()
    #Other_props.random_count
    #Other_props.use_originator_transform = True
    #Other_props.random_scale_min *= (Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3
    #Other_props.random_scale_max *= (Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3
    Other.set_properties(Other_props)

def Other_Safe_Zone(Other: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    Other_props: Other = Other.get_properties()
    EDITOR_PROPERTIES(Other_props.editor_properties, Other.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    COLOR(Other_props.normal_safe_zone_struct.shell_color, Other.id, rng)
    COLOR(Other_props.normal_safe_zone_struct.unknown_0xe68b1fa8, Other.id, rng)
    COLOR(Other_props.energized_safe_zone_struct.shell_color, Other.id, rng)
    COLOR(Other_props.energized_safe_zone_struct.unknown_0xe68b1fa8, Other.id, rng)
    COLOR(Other_props.supercharged_safe_zone_struct.shell_color, Other.id, rng)
    COLOR(Other_props.supercharged_safe_zone_struct.unknown_0xe68b1fa8, Other.id, rng)
    COLOR(Other_props.safe_zone_struct_a_0x8a09f99a.color, Other.id, rng)
    COLOR(Other_props.safe_zone_struct_a_0xafb855b8.color, Other.id, rng)
    Other.set_properties(Other_props)

def Enemy_Contraption(Other: ScriptInstanceHelper, editor: PatcherEditor, rng: random.Random, Range: dict):

    Data_Range = copy.deepcopy(Range)
    Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack = Randomize_Values(rng, Data_Range)
    #ACTOR = [0x180b0079, 0x180b007d, 0x180b0124, 0x180b0171, 0x180b01c7, 0x180b01cd, 0x180b0207]
    ACTORKEYFRAME = [0x180b01ec, 0x180b01ef, 0x180b01f7, 0x180b01f8, 0x180b01f9, 0x180b01fa, 0x180b01fb, 0x180b01fc]
    ACTORROTATE = [0x180b0100, 0x180b01fd, 0x180b0222]
    #PLATFORM = [0x180b0070, 0x180b0096, 0x180b0119, 0x180b012e, 0x180b0151, 0x180b015e, 0x180b01aa, 0x180b01bc, 0x180b01c3, 0x180b01cc]
    SEQUENCETIMER = [0x180b00e3, 0x180b01c8, 0x180b0224, 0x180b0236, 0x180b0370]
    TIMEKEYFRAME = [0x180b021d, 0x180b021e, 0x180b021f, 0x180b0220]
    TIMER = [0x180b0174, 0x180b017b, 0x180b017f, 0x180b018c, 0x180b018f, 0x180b019e, 0x180b01a1, 0x180b01c6, 0x180b01cb, 0x180b01cf, 0x180b01d6,
         0x180b0225, 0x180b0237, 0x180b0239, 0x180b0317, 0x180b0318, 0x180b0321, 0x180b0322, 0x180b0323, 0x180b0324, 0x180b0350, 0x180b0352,
         0x180b0356, 0x180b0357, 0x180b0375]
    for i in ACTORKEYFRAME:
        TEMP(editor, 'ACTOR_KEY_FRAME', MAIN_RESEARCH_MREA, i, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    for i in ACTORROTATE:
        TEMP(editor, 'ACTOR_ROTATE', MAIN_RESEARCH_MREA, i, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    for i in SEQUENCETIMER:
        TEMP(editor, 'SEQUENCE_TIMER', MAIN_RESEARCH_MREA, i, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    for i in TIMEKEYFRAME:
        TEMP(editor, 'TIME_KEY_FRAME', MAIN_RESEARCH_MREA, i, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
    for i in TIMER:
        TEMP(editor, 'TIMER', MAIN_RESEARCH_MREA, i, Range, rng, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack)
