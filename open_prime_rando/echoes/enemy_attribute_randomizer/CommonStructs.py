from open_prime_rando.echoes.enemy_attribute_randomizer.__init__ import Randomize_Values
import random

from open_prime_rando.patcher_editor import PatcherEditor

def EDITOR_PROPERTIES(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random, MIN=0.01, MAX=9999.0):

    if ID in [0x08200074, 0x08200040, 0x082e00b8, 0x08200075, 0x0820003f, 0x082e00b7]:
        return
    if ID in [0x081e0049, 0x0c03001c]:
        while all(i > 1.5 for i in Rand_Scale.values()):
            Rand_Scale = Randomize_Values(rng, Range)[0]
    #self.transform.position.x
    #self.transform.position.y
    #self.transform.position.z
		
    #self.transform.rotation.x
    #self.transform.rotation.y
    #self.transform.rotation.z

    while MIN > Rand_Scale['x'] > MAX:
        Rand_Scale['x'] = (Randomize_Values(rng, Range)[0])['x']
    self.transform.scale.x *= Rand_Scale['x']
    while MIN > Rand_Scale['y'] > MAX:
        Rand_Scale['y'] = (Randomize_Values(rng, Range)[0])['y']
    self.transform.scale.y *= Rand_Scale['y']
    while MIN > Rand_Scale['z'] > MAX:
        Rand_Scale['z'] = (Randomize_Values(rng, Range)[0])['z']
    self.transform.scale.z *= Rand_Scale['z']

def COLOR(self, ID, rng: random.Random):

    self.r = rng.random()
    self.g = rng.random()
    self.b = rng.random()
    self.a = rng.random()

def DAMAGE_INFO(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    #self.di_weapon_type
    self.di_damage *= Rand_Damage
    #self.di_radius
    self.di_knock_back_power *= Rand_KnockBack

def HEALTH(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    self.health *= Rand_Health
    self.hi_knock_back_resistance *= Rand_KnockBack

def PLASMA_BEAM_INFO(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    self.expansion_speed *= Rand_Speed
    self.life_time /= Rand_Speed
    self.pulse_speed *= Rand_Speed
    self.shutdown_time /= Rand_Speed
    self.contact_effect_scale *= (Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3
    self.pulse_effect_scale *= (Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3
    self.travel_speed *= Rand_Speed
    COLOR(self.inner_color, ID, rng)
    COLOR(self.inner_color, ID, rng)

def SHOCK_WAVE_INFO(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    DAMAGE_INFO(self.damage, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    #self.radial_velocity *= Rand_Speed
    #self.radial_velocity_acceleration *= Rand_Speed

def DAMAGE_VULNERABILITY(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    #TEMP_NAME:
        #damage_multiplier - float
        #effect - enums.Effect
        #ignore_radius - bool
	
    self.power.damage_multiplier
    self.dark.damage_multiplier
    self.light.damage_multiplier
    self.annihilator.damage_multiplier
    self.boost_ball.damage_multiplier
    self.cannon_ball.damage_multiplier
    self.screw_attack.damage_multiplier
    self.bomb.damage_multiplier
    self.power_bomb.damage_multiplier
    self.missile.damage_multiplier
    self.phazon.damage_multiplier
    self.ai.damage_multiplier
    self.poison_water.damage_multiplier
    self.dark_water.damage_multiplier
    self.lava.damage_multiplier
    self.area_damage_hot.damage_multiplier
    self.area_damage_cold.damage_multiplier
    self.area_damage_dark.damage_multiplier
    self.area_damage_light.damage_multiplier
    self.power_charge.damage_multiplier
    self.entangler.damage_multiplier
    self.light_blast.damage_multiplier
    self.sonic_boom.damage_multiplier
    self.super_missle.damage_multiplier
    self.black_hole.damage_multiplier
    self.sunburst.damage_multiplier
    self.imploder.damage_multiplier
    self.weapon_vulnerability.damage_multiplier
    self.normal_safe_zone.damage_multiplier
	
def PATTERNED(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    self.speed *= Rand_Speed
    self.turn_speed *= Rand_Speed
    self.average_attack_time /= Rand_Speed
    self.attack_time_variation /= Rand_Speed
    self.player_leash_time /= Rand_Speed

    DAMAGE_INFO(self.contact_damage, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)

    self.damage_wait_time /= Rand_Speed

    HEALTH(self.health, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
	
    DAMAGE_VULNERABILITY(self.vulnerability, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)

def BASIC_SWARM_PROPERTIES(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    DAMAGE_INFO(self.contact_damage, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    self.damage_wait_time /= Rand_Speed
    self.speed *= Rand_Speed
    #self.count
    #self.max_count
    self.spawn_speed *= Rand_Speed
    #self.attacker_count
    self.attack_timer /= Rand_Speed
    HEALTH(self.health, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    DAMAGE_VULNERABILITY(self.damage_vulnerability, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    self.turn_rate *= Rand_Speed
    self.freeze_duration /= Rand_Speed
    self.life_time /= Rand_Speed

def SANDWORM_STRUCT(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    self.unknown_0x98106ee2 *= Rand_Health #Health intervals for breaking his bomb throwing charge after you damage his tail.
    self.unknown_0x95081226 /= Rand_Speed #Delay between attacks
    self.unknown_0xc2064265 /= Rand_Speed #Delay between attacks
    self.move_speed_multiplier *= Rand_Speed
    if all(i > 1.0 for i in Rand_Scale.values()):
        Rand_Speed /= (Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3
    self.move_speed_multiplier *= Rand_Speed

def ING_POSSESSION_DATA(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    HEALTH(self.ing_possessed_health, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    #self.ing_possessed_damage_multiplier *= Rand_Damage
    DAMAGE_VULNERABILITY(self.ing_vulnerability, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)

def ING_SPACE_JUMP_GUARDIAN_STRUCT(self, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    self.locomotion_speed *= Rand_Speed
    self.unknown_0x3e370622 *= Rand_Health # health value before switching structs

def ING_BOOST_BALL_GUARDIAN_STRUCT(self, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    self.unknown_0x25d02bc5 /= Rand_Speed #default 15 seconds, wait time until start to go into ball form
    self.unknown_0x5d1626fb /= Rand_Speed #delays for attacking
    self.unknown_0xbb76891a /= Rand_Speed #delays for attacking
    self.locomotion_speed_scale *= (Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3
    self.ing_spot_speed_scale *= (Rand_Scale['x'] + Rand_Scale['y'] + Rand_Scale['z']) / 3

def ING_SPIDER_BALL_GUARDIAN_STRUCT(self, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    self.min_patrol_speed *= Rand_Speed
    self.max_patrol_speed *= Rand_Speed
    self.linear_acceleration *= Rand_Speed
    self.angular_speed *= Rand_Speed
    self.stunned_speed *= Rand_Speed
    #self.stunned_time /= Rand_Speed - bit to much
    #self.max_charge_time /= Rand_Speed - same as above

def POWER_BOMB_GUARDIAN_STAGE_PROPERTIES(self, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    self.unknown_0x95e7a2c2 /= Rand_Speed #min of range for random delay between attacks
    self.unknown_0x76ba1c18 /= Rand_Speed #Max of range for random delay between attacks
    self.unknown_0xbb4b6680 *= Rand_Speed #Speed of power bomb when thrown

def SWAMP_BOSS_STAGE2_STRUCT(self, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):
        
        self.health *= Rand_Health
        self.unknown_0x95e7a2c2 /= Rand_Speed # Attack delay
        self.unknown_0x76ba1c18 /= Rand_Speed # Attack delay
        self.unknown_0x29e6ead6 /= Rand_Speed # Attack delay
        self.unknown_0x1753225e /= Rand_Speed # Attack delay

def DIGITAL_GUARDIAN_HEAD_STRUCT(self, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    self.projectile_telegraph_time /= Rand_Speed
    self.projectile_attack_time /= Rand_Speed

def UNKNOWN_STRUCT17(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    #self.unknown_0xb5af7831 - Percentage of Dark Samus HP for it to transition to this stage
    self.unknown_struct17.unknown_0xac65eb7a /= Rand_Speed #Delay until attack
    self.unknown_struct17.unknown_0x4f3855a0 /= Rand_Speed #Delay until attack
    self.unknown_struct17.unknown_0x08c0b02c /= Rand_Speed #Delay until attack
    self.unknown_struct17.unknown_0x695f68c7 /= Rand_Speed #Delay until attack

def EMPEROR_ING_STAGE3_STRUCT_B(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    self.unknown_0x95e7a2c2 /= Rand_Speed # Min-Attack Delay
    self.unknown_0x76ba1c18 /= Rand_Speed # Max-Attack Delay
    #UNKNOWN_STRUCT2(self.unknown_struct2_0x3826ec75, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    #UNKNOWN_STRUCT2(self.unknown_struct2_0x93bf1106, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    #UNKNOWN_STRUCT2(self.unknown_struct2_0xc4b88b80, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    #UNKNOWN_STRUCT2(self.unknown_struct2_0x32c6dc77, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    #UNKNOWN_STRUCT2(self.unknown_struct2_0xc6e7b293, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    #UNKNOWN_STRUCT2(self.unknown_struct2_0x20746b56, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    #UNKNOWN_STRUCT2(self.unknown_struct2_0x2ab44adb, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    #UNKNOWN_STRUCT2(self.unknown_struct2_0xe2e78a78, Enemy.id, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)

#def UNKNOWN_STRUCT2(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    #enabled: bool = dataclasses.field(default=False)
    #chance: float = dataclasses.field(default=0.0)
    #modifier: float = dataclasses.field(default=0.0)

def SEQUENCE_TIMER(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):
    
    for c in self.sequence_connections:
        for t in c.activation_times:
            t /= Rand_Speed
    self.max_time /= Rand_Speed

def TIMER(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    self.time /= Rand_Speed
    self.random_adjust /= Rand_Speed

def ACTOR(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    EDITOR_PROPERTIES(self.editor_properties, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    #HEALTH(self)
    #DAMAGE_VULNERABILITY(self)
    #self.scale_animation - bool
    
def PLATFORM(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    EDITOR_PROPERTIES(self.editor_properties, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    #HEALTH(self)
    #DAMAGE_VULNERABILITY(self)

def ACTOR_KEY_FRAME(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    self.loop_duration /= Rand_Speed
    self.playback_rate *= Rand_Speed

def TIME_KEY_FRAME(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    self.time /= Rand_Speed

def ACTOR_ROTATE(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    self.duration /= Rand_Speed
    #rotation_controls: RotationSplines = dataclasses.field(default_factory=RotationSplines)
    #scale_controls: ScaleSplines = dataclasses.field(default_factory=ScaleSplines)

def EFFECT(self, ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range: dict, rng: random.Random):

    EDITOR_PROPERTIES(self.editor_properties, None, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    
def TEMP(editor: PatcherEditor, function_name, AREA_ID, INSTANCE_ID, Range: dict, rng: random.Random, Rand_Scale=1, Rand_Health=1, Rand_Speed=1, Rand_Damage=1, Rand_KnockBack=1):

    Temp = (editor.get_mrea(AREA_ID)).get_instance(INSTANCE_ID)
    Temp_props: Temp = Temp.get_properties()
    globals()[function_name](Temp_props, INSTANCE_ID, Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack, Range, rng)
    Temp.set_properties(Temp_props)
