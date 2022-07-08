from retro_data_structures.formats.script_object import ScriptInstanceHelper

def Enemy_Eye_Ball(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.close_time
    Enemy_props.fire_wait_time
    Enemy_props.ray_damage.DAMAGE_INFO
    Enemy_props.laser_inner_color.LASERCOLOR
    Enemy_props.laser_outer_color.LASERCOLOR
    Enemy.set_properties(Enemy_props)

def Enemy_Blogg(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.projectile_damage.DAMAGE_INFO
    Enemy_props.body_damage_multiplier
    Enemy_props.mouth_damage_multiplier
    Enemy_props.armor_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.charge_damage_radius
    Enemy_props.charge_damage
    Enemy_props.bite_damage
    Enemy_props.ball_spit_damage
    Enemy_props.charge_turn_speed
    Enemy_props.charge_speed_multiplier
    Enemy_props.ing_possession_data.ING_POSSESSION_DATA
    Enemy_props.ing_possessed_armor_vulnerability.DAMAGE_VULNERABILITY
    Enemy.set_properties(Enemy_props)

def Enemy_Flyer_Swarm(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.basic_swarm_properties.BASICS_WARM_PROPERTIES
    Enemy_props.roll_upright_speed
    Enemy.set_properties(Enemy_props)

def Enemy_Glowbug(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.attack_duration
    Enemy_props.attack_telegraph_duration
    Enemy.set_properties(Enemy_props)

def Enemy_Lumite(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.small_shot_damage.DAMAGE_INFO
    Enemy_props.big_shot_damage.DAMAGE_INFO
    Enemy.set_properties(Enemy_props)

def Enemy_Mystery_Flyer(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.mystery_flyer_properties.shot_damage
    Enemy_props.mystery_flyer_properties.hover_speed
    Enemy.set_properties(Enemy_props)

def Enemy_Shrieker(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.buried_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.damage_info.DAMAGE_INFO
    Enemy_props.projectile_damage.DAMAGE_INFO
    Enemy_props.melee_damage.DAMAGE_INFO
    Enemy_props.melee_attack_time_variation
    Enemy_props.dodge_time
    Enemy_props.visibility_change_time
    Enemy.set_properties(Enemy_props)

def Enemy_Metaree(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.radius_damage.DAMAGE_INFO
    Enemy_props.attack_speed
    Enemy_props.drop_delay
    Enemy_props.halt_delay
    Enemy_props.launch_speed
    Enemy.set_properties(Enemy_props)

def Enemy_Shredder(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.data.explosion_damage.DAMAGE_INFO
    Enemy_props.data.min_life_time
    Enemy_props.data.max_life_time
    Enemy_props.data.normal_knockback
    Enemy_props.data.heavy_knockback
    Enemy_props.data.knockback_decline
    Enemy.set_properties(Enemy_props)

def Enemy_Pillbug(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.floor_turn_speed
    Enemy_props.damage_vulnerability.DAMAGE_INFO
    Enemy_props.wander_vulnerability.DAMAGE_INFO
    Enemy.set_properties(Enemy_props)

def Enemy_Brizgee(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.wall_turn_speed
    Enemy_props.floor_turn_speed
    Enemy_props.down_turn_speed
    Enemy_props.shell_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.shell_health
    Enemy_props.shell_contact_damage.DAMAGE_INFO
    Enemy_props.poison_damage.DAMAGE_INFO
    Enemy_props.poison_time
    Enemy.set_properties(Enemy_props)

def Enemy_Kralee(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.wall_turn_speed
    Enemy_props.floor_turn_speed
    Enemy_props.down_turn_speed
    Enemy_props.warp_in_time
    Enemy_props.warp_out_time
    Enemy_props.visible_time
    Enemy_props.invisible_time
    Enemy_props.warp_attack_radius
    Enemy_props.warp_attack_knockback
    Enemy_props.warp_attack_damage
    Enemy_props.anim_speed_scalar
    Enemy.set_properties(Enemy_props)

def Enemy_Plant_Scarab_Swarm(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.basic_swarm_properties.BASICS_WARM_PROPERTIES
    Enemy_props.into_attack_speed
    Enemy_props.attack_speed
    Enemy_props.grenade_launch_speed
    Enemy_props.grenade_damage.DAMAGE_INFO
    Enemy.set_properties(Enemy_props)

def Enemy_Krocuss(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.wall_turn_speed
    Enemy_props.floor_turn_speed
    Enemy_props.down_turn_speed
    Enemy_props.anim_speed_scalar
    Enemy_props.shell_closed_vulnerability.DAMAGE_VULNERABILITY
    Enemy.set_properties(Enemy_props)

def Enemy_Crystallite(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.wall_turn_speed
    Enemy_props.floor_turn_speed
    Enemy_props.down_turn_speed
    Enemy_props.stun_time
    Enemy.set_properties(Enemy_props)

def Enemy_Sandworm(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.pincer_scale
    Enemy_props.projectile_damage.DAMAGE_INFO
    Enemy_props.morphball_toss_damage.DAMAGE_INFO
    Enemy_props.pincer_swipe_damage.DAMAGE_INFO
    Enemy_props.pursuit_frustration_timer
    Enemy_props.ing_boss_bomb_damage.DAMAGE_INFO
    Enemy_props.ing_possession_data.ING_POSSESSION_DATA
    Enemy.set_properties(Enemy_props)

def Enemy_Grenchler(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.damage_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.bite_damage.DAMAGE_INFO
    Enemy_props.beam_damage.DAMAGE_INFO
    Enemy_props.burst_damage.DAMAGE_INFO
    Enemy_props.grapple_damage.DAMAGE_INFO
    Enemy_props.damage_info.DAMAGE_INFO
    Enemy_props.ing_possession_data.ING_POSSESSION_DATA
    Enemy.set_properties(Enemy_props)

def Enemy_Sporb_Base(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.grabber_out_acceleration
    Enemy_props.grabber_in_acceleration
    Enemy_props.grabber_attach_time
    Enemy_props.spit_force
    Enemy_props.spit_damage
    Enemy_props.grab_damage
    Enemy_props.power_bomb_projectile_damage.DAMAGE_INFO
    Enemy.set_properties(Enemy_props)

def Enemy_Splinter(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.attack_damage.DAMAGE_INFO
    Enemy_props.damage_info_0x4436a388.DAMAGE_INFO
    Enemy_props.ing_possession_data.ING_POSSESSION_DATA
    Enemy.set_properties(Enemy_props)

def Enemy_Atomic_Alpha(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.bomb_damage.DAMAGE_INFO
    Enemy_props.bomb_drop_delay
    Enemy_props.bomb_reappear_delay
    Enemy_props.bomb_reappear_time
    Enemy.set_properties(Enemy_props)

def Enemy_Tryclops(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.attract_force
    Enemy_props.shot_force
    Enemy.set_properties(Enemy_props)

def Enemy_Atomic_Beta(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.beam_damage.DAMAGE_INFO
    Enemy_props.beam_fade_time
    Enemy_props.hover_speed
    Enemy_props.frozen_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.normal_rotate_speed
    Enemy_props.charging_rotate_speed
    Enemy_props.speed_change_rate
    Enemy_props.damage_delay
    Enemy.set_properties(Enemy_props)

def Enemy_Metaree_Swarm(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.basic_swarm_properties.BASICS_WARM_PROPERTIES
    Enemy_props.into_attack_speed
    Enemy_props.attack_speed
    Enemy.set_properties(Enemy_props)

def Enemy_Rezbit(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.rezbit_data.shield_down_time
    Enemy_props.rezbit_data.shield_up_time
    Enemy_props.rezbit_data.energy_bolt_damage.DAMAGE_INFO
    Enemy_props.rezbit_data.energy_bolt_attack_duration
    Enemy_props.rezbit_data.virus_attack_time
    Enemy_props.rezbit_data.virus_damage.DAMAGE_INFO
    Enemy_props.rezbit_data.cutting_laser_damage.DAMAGE_INFO
    Enemy_props.rezbit_data.cutting_laser_beam_info.PLASMA_BEAM_INFO
    Enemy_props.rezbit_data.shield_vulnerability.DAMAGE_VULNERABILITY
    Enemy.set_properties(Enemy_props)

def Enemy_Octapede_Segment(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.wall_turn_speed
    Enemy_props.floor_turn_speed
    Enemy_props.down_turn_speed
    Enemy_props.anim_speed_scalar
    Enemy_props.explosion_damage.DAMAGE_INFO
    Enemy.set_properties(Enemy_props)

def Enemy_AI_Manned_Turret(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.unknown_struct3.horiz_speed
    Enemy_props.unknown_struct3.vert_speed
    Enemy_props.unknown_struct3.fire_rate
    Enemy_props.unknown_struct3.attack_leash_timer
    Enemy_props.unknown_struct3.weapon_damage.DAMAGE_INFO
    Enemy_props.unknown_struct3.health.HEALTH
    Enemy_props.unknown_struct3.vulnerability.DAMAGE_VULNERABILITY
    Enemy.set_properties(Enemy_props)

#Caretaker Class Drone - Bunch Of Actors

def Enemy_Gun_Turret_Base(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.attack_damage.DAMAGE_INFO
    Enemy_props.hurt_sleep_delay
    Enemy_props.gun_aim_turn_speed
    Enemy_props.patrol_delay
    Enemy_props.withdraw_delay
    Enemy_props.attack_delay
    Enemy_props.attack_leash_time
    Enemy.set_properties(Enemy_props)

def Enemy_Gun_Turret_Top(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.power_up_time
    Enemy_props.power_down_time
    Enemy_props.light_color.COLOR
    Enemy.set_properties(Enemy_props)

def Enemy_Elite_Pirate(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.melee_damage.DAMAGE_INFO
    Enemy_props.taunt_interval
    Enemy_props.taunt_variance
    Enemy_props.single_shock_wave_info.SHOCK_WAVE_INFO
    Enemy_props.double_shock_wave_info.SHOCK_WAVE_INFO
    Enemy_props.rocket_damage.DAMAGE_INFO
    Enemy_props.energy_absorb_duration
    Enemy_props.ing_possession_data.ING_POSSESSION_DATA
    Enemy.set_properties(Enemy_props)

#Watchdrone - StoneToad - STOD - NONE

def Enemy_Wall_Walker(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.leg_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.floor_turn_speed
    Enemy_props.explode_damage.DAMAGE_INFO
    Enemy_props.projectile_interval
    Enemy_props.projectile_damage
    Enemy.set_properties(Enemy_props)

def Enemy_Splitter_Command_Module(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.unknown_struct43.max_linear_velocity
    Enemy_props.unknown_struct43.max_turn_speed
    Enemy_props.unknown_struct43.scanning_turn_speed
    Enemy_props.unknown_struct43.laser_pulse_damage.DAMAGE_INFO
    Enemy_props.unknown_struct43.reset_shield_time
    Enemy_props.unknown_struct43.laser_sweep_turn_speed
    Enemy_props.unknown_struct43.laser_sweep_damage.DAMAGE_INFO
    Enemy_props.unknown_struct43.laser_sweep_beam_info.PLASMA_BEAM_INFO
    Enemy_props.unknown_struct43.unknown_struct42.cloud_color1.COLOR
    Enemy_props.unknown_struct43.unknown_struct42.cloud_color2.COLOR
    Enemy_props.unknown_struct43.unknown_struct42.add_color1.COLOR
    Enemy_props.unknown_struct43.unknown_struct42.add_color2.COLOR
    Enemy_props.unknown_struct43.unknown_struct42.cloud_scale
    Enemy_props.unknown_struct43.unknown_struct42.fade_off_size
    Enemy_props.unknown_struct43.unknown_struct42.open_speed
    Enemy_props.unknown_struct43.ing_possession_data.ING_POSSESSION_DATA
    Enemy_props.unknown_struct43.light_shield_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.unknown_struct43.dark_shield_vulnerability.DAMAGE_VULNERABILITY
    Enemy.set_properties(Enemy_props)

def Enemy_Splitter_Main_Chassis(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.splitter_main_chassis_data.leg_stab_attack_interval
    Enemy_props.splitter_main_chassis_data.leg_stab_damage.DAMAGE_INFO
    Enemy_props.splitter_main_chassis_data.min_dodge_interval
    Enemy_props.splitter_main_chassis_data.deployment_speed
    Enemy_props.splitter_main_chassis_data.scan_duration
    Enemy_props.splitter_main_chassis_data.laser_sweep_interval
    Enemy_props.splitter_main_chassis_data.spin_attack_interval
    Enemy_props.splitter_main_chassis_data.spin_attack_damage
    Enemy_props.splitter_main_chassis_data.ing_possession_data.ING_POSSESSION_DATA
    Enemy_props.splitter_main_chassis_data.spin_attack_vulnerability.DAMAGE_VULNERABILITY
    Enemy.set_properties(Enemy_props)

def Enemy_Bacteria_Swarm(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.basic_swarm_properties.BASICS_WARM_PROPERTIES
    Enemy_props.bacteria_patrol_speed
    Enemy_props.bacteria_acceleration
    Enemy_props.bacteria_deceleration
    Enemy_props.patrol_turn_speed
    Enemy_props.bacteria_patrol_color.COLOR
    Enemy_props.bacteria_player_pursuit_color.COLOR
    Enemy_props.color_change_time
    Enemy.set_properties(Enemy_props)

def Enemy_Minor_Ing(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.projectile_damage.DAMAGE_INFO
    Enemy_props.unknown_struct33.damage.DAMAGE_INFO
    Enemy_props.unknown_struct33.bomb_stun_duration
    Enemy_props.unknown_struct33.max_speed
    Enemy_props.unknown_struct33.max_wall_speed
    Enemy_props.unknown_struct33.ball_pursuit_speed
    Enemy_props.unknown_struct33.speed_modifier
    Enemy_props.unknown_struct33.turn_speed
    Enemy_props.unknown_struct33.hit_normal_damage
    Enemy_props.unknown_struct33.hit_heavy_damage
    Enemy_props.unknown_struct33.vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.unknown_struct34.health.HEALTH
    Enemy_props.unknown_struct34.damage.DAMAGE_INFO
    Enemy_props.unknown_struct34.min_launch_speed
    Enemy_props.unknown_struct34.max_launch_speed
    Enemy_props.unknown_struct34.min_generation
    Enemy_props.unknown_struct34.max_generation
    Enemy.set_properties(Enemy_props)

def Enemy_Ing(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.ing_spot_max_speed
    Enemy_props.ing_spot_turn_speed
    Enemy_props.ing_spot_hit_normal_damage
    Enemy_props.ing_spot_hit_heavy_damage
    Enemy_props.frustration_time
    Enemy_props.arm_swipe_damage.DAMAGE_INFO
    Enemy_props.body_projectile_contact_damage.DAMAGE_INFO
    Enemy_props.body_projectile_suck_time
    Enemy_props.body_projectile_speed
    Enemy_props.body_projectile_drop_time
    Enemy_props.mini_portal_projectile_damage.DAMAGE_INFO
    Enemy_props.mini_portal_beam_info.PlasmaBeamInfo
    Enemy_props.exit_grapple_damage.DAMAGE_INFO
    Enemy_props.exit_grapple_spit_force
    Enemy_props.light_color.COLOR
    Enemy_props.ing_spot_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.grapple_ball_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.trigger_vulnerability.DAMAGE_VULNERABILITY
    Enemy.set_properties(Enemy_props)

def Enemy_Ing_Blob_Swarm(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.basic_swarm_properties.BASICS_WARM_PROPERTIES
    Enemy_props.into_attack_speed
    Enemy_props.attack_speed
    Enemy.set_properties(Enemy_props)

def Enemy_Wisp_Tentacle(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.attack_damage.DAMAGE_INFO
    Enemy_props.hurt_sleep_delay
    Enemy_props.grab_blend_time
    Enemy.set_properties(Enemy_props)

def Enemy_Medium_Ing(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.min_melee_attack_interval
    Enemy_props.melee_damage.DAMAGE_INFO
    Enemy_props.mist_damage.DAMAGE_INFO
    Enemy_props.min_mist_attack_interval
    Enemy_props.misting_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.min_arm_attack_interval
    Enemy_props.arm_attack_time
    Enemy_props.attack_tentacle_damage.DAMAGE_INFO
    Enemy_props.light_color.COLOR
    Enemy_props.dash_speed
    Enemy.set_properties(Enemy_props)

def Enemy_Digital_Guardian(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.digital_guardian_data.leg_stab_damage.DAMAGE_INFO
    Enemy_props.digital_guardian_data.shock_wave_info.SHOCK_WAVE_INFO
    Enemy_props.digital_guardian_data.vortex_attack_duration
    Enemy_props.digital_guardian_data.vortex_attraction_force
    Enemy_props.digital_guardian_data.vortex_linear_velocity
    Enemy_props.digital_guardian_data.vortex_linear_acceleration
    Enemy_props.digital_guardian_data.vortex_damage.DAMAGE_INFO
    Enemy_props.digital_guardian_data.jump_timer
    Enemy_props.digital_guardian_data.knee_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.digital_guardian_data.vortex_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.digital_guardian_data.toe_target_vulnerability.DAMAGE_VULNERABILITY
    Enemy.set_properties(Enemy_props)

def Enemy_Digital_Guardian_Head(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.digital_guardian_head_data.max_turn_speed
    Enemy_props.digital_guardian_head_data.max_linear_velocity
    Enemy_props.digital_guardian_head_data.plasma_beam_info.PLASMA_BEAM_INFO
    Enemy_props.digital_guardian_head_data.lock_on_missiles_damage.DAMAGE_INFO
    Enemy_props.digital_guardian_head_data.machine_gun_damage.DAMAGE_INFO
    Enemy_props.digital_guardian_head_data.digital_guardian_head_struct_0x8f6732ea.DIGITAL_GUARDIAN_HEAD_STRUCT
    Enemy_props.digital_guardian_head_data.digital_guardian_head_struct_0x8e128141.DIGITAL_GUARDIAN_HEAD_STRUCT
    Enemy_props.digital_guardian_head_data.digital_guardian_head_struct_0xea54b390.DIGITAL_GUARDIAN_HEAD_STRUCT
    Enemy_props.digital_guardian_head_data.digital_guardian_head_struct_0xbbd3e7a7.DIGITAL_GUARDIAN_HEAD_STRUCT
    Enemy_props.digital_guardian_head_data.digital_guardian_head_struct_0x2dd88764.DIGITAL_GUARDIAN_HEAD_STRUCT
    Enemy_props.digital_guardian_head_data.digital_guardian_head_struct_0x48b46e55.DIGITAL_GUARDIAN_HEAD_STRUCT
    Enemy_props.digital_guardian_head_data.bomb_pit_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.digital_guardian_head_data.echo_target_vulnerability.DAMAGE_VULNERABILITY
    Enemy.set_properties(Enemy_props)

def Enemy_Ing_Space_Jump_Guardian(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.unknown_struct32.ing_space_jump_guardian_struct_0x5e1d1931.ING_SPACE_JUMP_GUARDIAN_STRUCT
    Enemy_props.unknown_struct32.ing_space_jump_guardian_struct_0x6b08e2e5.ING_SPACE_JUMP_GUARDIAN_STRUCT
    Enemy_props.unknown_struct32.ing_space_jump_guardian_struct_0xf223aa76.ING_SPACE_JUMP_GUARDIAN_STRUCT
    Enemy_props.unknown_struct32.ing_space_jump_guardian_struct_0xd0db5f7a.ING_SPACE_JUMP_GUARDIAN_STRUCT
    Enemy.set_properties(Enemy_props)

def Enemy_Ing_Boost_Ball_Guardian(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.unknown_struct28.ing_spot_max_speed
    Enemy_props.unknown_struct28.ing_spot_turn_speed
    Enemy_props.unknown_struct28.ing_spot_hit_normal_damage
    Enemy_props.unknown_struct28.ing_spot_hit_heavy_damage
    Enemy_props.unknown_struct28.frustration_time
    Enemy_props.unknown_struct28.arm_swipe_damage.DAMAGE_INFO
    Enemy_props.unknown_struct28.body_projectile_contact_damage.DAMAGE_INFO
    Enemy_props.unknown_struct28.body_projectile_suck_time
    Enemy_props.unknown_struct28.body_projectile_speed
    Enemy_props.unknown_struct28.body_projectile_drop_time
    Enemy_props.unknown_struct28.mini_portal_projectile_damage.DAMAGE_INFO
    Enemy_props.unknown_struct28.mini_portal_beam_info.PLASMA_BEAM_INFO
    Enemy_props.unknown_struct28.light_color.COLOR
    Enemy_props.unknown_struct28.ing_spot_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.unknown_struct29.boost_ball_scale
    Enemy_props.unknown_struct29.boost_ball_speed
    Enemy_props.unknown_struct29.damage_info_0x0e1a78bd.DAMAGE_INFO
    Enemy_props.unknown_struct29.damage_info_0x19c3d263.DAMAGE_INFO
    Enemy_props.unknown_struct29.boost_ball_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.unknown_struct29.damage_info_0x5616d5f1.DAMAGE_INFO
    Enemy_props.unknown_struct29.damage_info_0xed685533.DAMAGE_INFO
    Enemy_props.unknown_struct29.ing_boost_ball_guardian_struct_0xbab98497.ING_BOOST_BALL_GUARDIAN_STRUCT
    Enemy_props.unknown_struct29.ing_boost_ball_guardian_struct_0xfe18a18f.ING_BOOST_BALL_GUARDIAN_STRUCT
    Enemy_props.unknown_struct29.ing_boost_ball_guardian_struct_0xc2784287.ING_BOOST_BALL_GUARDIAN_STRUCT
    Enemy.set_properties(Enemy_props)

def Enemy_Ing_Spider_ball_Guardian(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.unknown_struct31.ing_spiderball_guardian_struct_0x152db484.ING_SPIDER_BALL_GUARDIAN_STRUCT
    Enemy_props.unknown_struct31.ing_spiderball_guardian_struct_0x2d163ff7.ING_SPIDER_BALL_GUARDIAN_STRUCT
    Enemy_props.unknown_struct31.ing_spiderball_guardian_struct_0x8c2fbb19.ING_SPIDER_BALL_GUARDIAN_STRUCT
    Enemy_props.unknown_struct31.ing_spiderball_guardian_struct_0x5d612911.ING_SPIDER_BALL_GUARDIAN_STRUCT
    Enemy_props.unknown_struct31.ing_spiderball_guardian_struct_0xfc58adff.ING_SPIDER_BALL_GUARDIAN_STRUCT
    Enemy_props.unknown_struct31.ing_spiderball_guardian_struct_0xc463268c.ING_SPIDER_BALL_GUARDIAN_STRUCT
    Enemy_props.unknown_struct31.proximity_damage.DAMAGE_INFO
    Enemy.set_properties(Enemy_props)

def Enemy_Sand_Boss(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.sand_boss_data.snap_jaw_damage.DAMAGE_INFO
    Enemy_props.sand_boss_data.spit_out_damage.DAMAGE_INFO
    Enemy_props.sand_boss_data.dark_beam_damage.DAMAGE_INFO
    Enemy_props.sand_boss_data.suck_air_time
    Enemy_props.sand_boss_data.spit_morphball_time
    Enemy_props.sand_boss_data.unknown_struct40.damage_info.DAMAGE_INFO
    Enemy_props.sand_boss_data.unknown_struct41.sand_boss_struct_b_0xb9784f0e.damage.DAMAGE_INFO
    Enemy_props.sand_boss_data.unknown_struct41.sand_boss_struct_b_0xb9784f0e.duration
    Enemy_props.sand_boss_data.unknown_struct41.sand_boss_struct_b_0xb9784f0e.change_direction_interval
    Enemy_props.sand_boss_data.unknown_struct41.sand_boss_struct_b_0xb9784f0e.turn_speed
    Enemy_props.sand_boss_data.unknown_struct41.sand_boss_struct_b_0xb8ae1bdc.damage.DAMAGE_INFO
    Enemy_props.sand_boss_data.unknown_struct41.sand_boss_struct_b_0xb8ae1bdc.duration
    Enemy_props.sand_boss_data.unknown_struct41.sand_boss_struct_b_0xb8ae1bdc.change_direction_interval
    Enemy_props.sand_boss_data.unknown_struct41.sand_boss_struct_b_0xb8ae1bdc.turn_speed
    Enemy_props.sand_boss_data.unknown_struct41.charge_beam_info.PlasmaBeamInfo
    Enemy_props.sand_boss_data.damage_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.sand_boss_data.stampede_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.sand_boss_data.suck_air_vulnerability.DAMAGE_VULNERABILITY
    Enemy.set_properties(Enemy_props)

def Enemy_Swamp_Boss_Stage_1(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.unknown_struct37.splash_shock_wave.SHOCK_WAVE_INFO
    Enemy_props.unknown_struct37.damage_info.DAMAGE_INFO
    Enemy_props.unknown_struct37.weak_spot_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.unknown_struct37.weak_spot_damage_multiplier
    Enemy_props.unknown_struct37.spit_damage
    Enemy.set_properties(Enemy_props)

def Enemy_Swamp_Boss_Stage_2(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.ing_possession_data.ING_POSSESSION_DATA
    Enemy_props.swamp_boss_stage2_data.hover_speed
    Enemy_props.swamp_boss_stage2_data.swamp_boss_stage2_struct_0x7fa9256a.health.HEALTH
    Enemy_props.swamp_boss_stage2_data.swamp_boss_stage2_struct_0x8b884b8e.health.HEALTH
    Enemy_props.swamp_boss_stage2_data.swamp_boss_stage2_struct_0x04b7a789.health.HEALTH
    Enemy_props.swamp_boss_stage2_data.swamp_boss_stage2_struct_0xf096c96d.health.HEALTH
    Enemy_props.swamp_boss_stage2_data.stun_time
    Enemy_props.swamp_boss_stage2_data.spit_damage.DAMAGE_INFO
    Enemy_props.swamp_boss_stage2_data.swoop_damage.DAMAGE_INFO
    Enemy_props.swamp_boss_stage2_data.swoop_damage_time
    Enemy_props.swamp_boss_stage2_data.splash_shock_wave.SHOCK_WAVE_INFO
    Enemy_props.swamp_boss_stage2_data.unknown_struct38.turn_rate
    Enemy_props.swamp_boss_stage2_data.unknown_struct38.warp_scale
    Enemy_props.swamp_boss_stage2_data.blow_damage.DAMAGE_INFO
    Enemy_props.swamp_boss_stage2_data.break_stun_damage
    Enemy.set_properties(Enemy_props)


#Emperor Ing Stage 1 - EmperorIngStage1 - EMS1 - TODO
#Emperor Ing Stage 2 Tentacle - EmperorIngStage2Tentacle - EM2T - TODO
#Emperor Ing Stage 3 - EmperorIngStage3 - EMS3 - TODO
    
def Enemy_Puddle_Spore(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.charge_time
    Enemy_props.time_open
    Enemy_props.platform_time
    Enemy_props.shock_wave_info.SHOCK_WAVE_INFO
    Enemy.set_properties(Enemy_props)

def Enemy_Dark_Commando(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.dark_commando_properties.blade_damage.DAMAGE_INFO
    Enemy_props.dark_commando_properties.unknown_struct12.grenade_damage.DAMAGE_INFO
    Enemy_props.dark_commando_properties.unknown_struct13.damage.DAMAGE_INFO
    Enemy_props.dark_commando_properties.unknown_struct13.mold_damage.DAMAGE_INFO
    Enemy_props.dark_commando_properties.unknown_struct14.shadow_dash_speed
    Enemy_props.dark_commando_properties.unknown_struct14.shadow_decoy_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.dark_commando_properties.unknown_struct14.shadow_dash_vulnerability.DAMAGE_VULNERABILITY
    Enemy.set_properties(Enemy_props)

def Enemy_Dark_Trooper(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.ing_possession_data.ING_POSSESSION_DATA
    Enemy_props.melee_attack_damage.DAMAGE_INFO
    Enemy_props.ranged_attack_damage.DAMAGE_INFO
    Enemy_props.missile_damage.DAMAGE_INFO
    Enemy.set_properties(Enemy_props)

def Enemy_Puffer(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.hover_speed
    Enemy_props.cloud_damage.DAMAGE_INFO
    Enemy_props.explosion_damage.DAMAGE_INFO
    Enemy.set_properties(Enemy_props)

def Enemy_Space_Pirate(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.ing_possession_data.ING_POSSESSION_DATA
    Enemy_props.projectile_damage.DAMAGE_INFO
    Enemy_props.blade_damage.DAMAGE_INFO
    Enemy_props.kneel_attack_damage.DAMAGE_INFO
    Enemy_props.gun_track_delay
    #weapon_data
    Enemy.set_properties(Enemy_props)

def Enemy_Commando_Pirate(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.ing_possession_data.ING_POSSESSION_DATA
    Enemy_props.blade_damage.DAMAGE_INFO
    Enemy_props.projectile_damage.DAMAGE_INFO
    Enemy_props.unknown_struct10.grenade_min_attack_interval
    Enemy_props.unknown_struct10.grenade_damage.DAMAGE_INFO
    Enemy_props.unknown_struct11.shield_charge_damage.DAMAGE_INFO
    Enemy_props.unknown_struct11.shield_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.unknown_struct11.shield_charge_speed
    Enemy_props.unknown_struct11.arm_shield_time
    Enemy.set_properties(Enemy_props)

def Enemy_Flying_Pirate(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.projectile_damage.DAMAGE_INFO
    Enemy_props.missile_damage.DAMAGE_INFO
    Enemy_props.hurl_recover_time
    Enemy_props.hover_height
    Enemy_props.rocket_pack_explosion_damage.DAMAGE_INFO
    Enemy_props.minimum_missile_time
    Enemy.set_properties(Enemy_props)

def Enemy_Metroid_Alpha(Enemy: ScriptInstanceHelper):

    Enemy_props: Enemy = Enemy.get_properties()
    Enemy_props.frozen_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.energy_drain_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.damage_vulnerability.DAMAGE_VULNERABILITY
    Enemy_props.telegraph_attack_time
    Enemy_props.baby_metroid_scale
    Enemy_props.ing_possession_data.ING_POSSESSION_DATA
    Enemy.set_properties(Enemy_props)

#Dark Samus (four forms) - TODO
