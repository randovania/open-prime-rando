from random import Random
import random
import pickle as pkl
from retro_data_structures.enums import echoes
from retro_data_structures.formats.script_object import ScriptInstanceHelper
from retro_data_structures.formats import Mlvl

from open_prime_rando.echoes.asset_ids import world as world_ids
from open_prime_rando.patcher_editor import PatcherEditor
from open_prime_rando.echoes.enemy_attribute_randomizer.EnemyTypes import EnemyTypes
from open_prime_rando.echoes.enemy_attribute_randomizer.EnemyTypes import OtherTypes
from open_prime_rando.echoes.enemy_attribute_randomizer.EnemyProperties import *

_WORLDS = [
    world_ids.TEMPLE_GROUNDS_MLVL, world_ids.AGON_WASTES_MLVL, world_ids.TORVUS_BOG_MLVL,
    world_ids.SANCTUARY_FORTRESS_MLVL, world_ids.GREAT_TEMPLE_MLVL,
]
_AREAS_TO_SKIP = {
    0x775664a5,  # 00_scandummy
    0x752b2850,  # game_end_part1
    0x9d221f4a,  # game_end_part2
    0xc5250dbc,  # game_end_part3
    0x9641773f,  # game_end_part4
    0xce4665c9,  # game_end_part5
    0x4d4e5400,  # Menu
}

def Randomize_Values(rng: random.Random, Range: dict):

    Rand_Scale = {'x': None, 'y': None, 'z': None}
    Rand_Scale['x'] = rng.uniform(Range["SC_Low"], Range["SC_High"])
    if Range["DIFF_XYZ"]:
        Rand_Scale['y'] = rng.uniform(Range["SC_Low"], Range["SC_High"])
        Rand_Scale['z'] = rng.uniform(Range["SC_Low"], Range["SC_High"])
    else:
        Rand_Scale['y'] = Rand_Scale['x']
        Rand_Scale['z'] = Rand_Scale['x']
    Rand_Health = rng.uniform(Range["H_Low"], Range["H_High"])
    Rand_Speed = rng.uniform(Range["SP_Low"], Range["SP_High"])
    Rand_Damage = rng.uniform(Range["D_Low"], Range["D_High"])
    Rand_KnockBack = rng.uniform(Range["K_Low"], Range["K_High"])
    return Rand_Scale, Rand_Health, Rand_Speed, Rand_Damage, Rand_KnockBack

def Make_Changes(editor: PatcherEditor):
    rng = Random(79087239846)
    Scale_Low = 0.25
    Scale_High = 0.5
    Health_Low = 0.25
    Health_High = 0.5
    Speed_Low = 4.0
    Speed_High = 10.0
    Damage_Low = 0.25
    Damage_High = 0.25
    KnockBack_Low = 0.25
    KnockBack_High = 0.5
    diff_xyz_scale = False
    Range_Dict = {"SC_Low": Scale_Low, "SC_High": Scale_High, "H_Low": Health_Low, "H_High": Health_High,
                  "SP_Low": Speed_Low, "SP_High": Speed_High, "D_Low": Damage_Low, "D_High": Damage_High,
                  "K_Low": KnockBack_Low, "K_High": KnockBack_High, "DIFF_XYZ": diff_xyz_scale}
    From_File = True
    Function_Names = ['Enemy_Eye_Ball', 'Enemy_Blogg', 'Enemy_Flyer_Swarm', 'Enemy_Glowbug', 'Enemy_Lumite',
                      'Enemy_Mystery_Flyer', 'Enemy_Shrieker', 'Enemy_Metaree',
                      'Enemy_Shredder', 'Enemy_Pillbug', 'Enemy_Brizgee', 'Enemy_Kralee', 'Enemy_Plant_Scarab_Swarm',
                      'Enemy_Krocuss', 'Enemy_Crystallite', 'Enemy_Sandworm',
                      'Enemy_Grenchler', 'Enemy_Sporb_Base', 'Enemy_Splinter', 'Enemy_Atomic_Alpha', 'Enemy_Tryclops',
                      'Enemy_Atomic_Beta', 'Enemy_Metaree_Swarm', 'Enemy_Rezbit',
                      'Enemy_Octapede_Segment', 'Enemy_AI_Manned_Turret', 'Enemy_Gun_Turret_Base',
                      'Enemy_Gun_Turret_Top', 'Enemy_Elite_Pirate', 'Enemy_Wall_Walker',
                      'Enemy_Splitter_Command_Module',
                      'Enemy_Splitter_Main_Chassis', 'Enemy_Bacteria_Swarm', 'Enemy_Minor_Ing', 'Enemy_Ing',
                      'Enemy_Ing_Blob_Swarm', 'Enemy_Wisp_Tentacle', 'Enemy_Medium_Ing',
                      'Enemy_Digital_Guardian', 'Enemy_Digital_Guardian_Head', 'Enemy_Ing_Space_Jump_Guardian',
                      'Enemy_Ing_Boost_Ball_Guardian', 'Enemy_Ing_Spider_ball_Guardian',
                      'Enemy_Sand_Boss', 'Enemy_Swamp_Boss_Stage_1', 'Enemy_Swamp_Boss_Stage_2',
                      'Enemy_Emperor_Ing_Stage_1', 'Enemy_Emperor_Ing_Stage_2', 'Enemy_Emperor_Ing_Stage_3',
                      'Enemy_Puddle_Spore', 'Enemy_Dark_Commando', 'Enemy_Dark_Trooper', 'Enemy_Puffer',
                      'Enemy_Space_Pirate', 'Enemy_Commando_Pirate', 'Enemy_Flying_Pirate',
                      'Enemy_Metroid_Alpha', 'Enemy_Dark_Samus', 'Other_Color_Modulate', 'Other_Generator',
                      'Other_Safe_Zone']
    if not From_File:
        Props_Enemy_Eye_Ball = {}
        Props_Enemy_Blogg = {}
        Props_Enemy_Flyer_Swarm = {}
        Props_Enemy_Glowbug = {}
        Props_Enemy_Lumite = {}
        Props_Enemy_Mystery_Flyer = {}
        Props_Enemy_Shrieker = {}
        Props_Enemy_Metaree = {}
        Props_Enemy_Shredder = {}
        Props_Enemy_Pillbug = {}
        Props_Enemy_Brizgee = {}
        Props_Enemy_Kralee = {}
        Props_Enemy_Plant_Scarab_Swarm = {}
        Props_Enemy_Krocuss = {}
        Props_Enemy_Crystallite = {}
        Props_Enemy_Sandworm = {}
        Props_Enemy_Grenchler = {}
        Props_Enemy_Sporb_Base = {}
        Props_Enemy_Splinter = {}
        Props_Enemy_Atomic_Alpha = {}
        Props_Enemy_Tryclops = {}
        Props_Enemy_Atomic_Beta = {}
        Props_Enemy_Metaree_Swarm = {}
        Props_Enemy_Rezbit = {}
        Props_Enemy_Octapede_Segment = {}
        Props_Enemy_AI_Manned_Turret = {}
        Props_Enemy_Gun_Turret_Base = {}
        Props_Enemy_Gun_Turret_Top = {}
        Props_Enemy_Elite_Pirate = {}
        #Props_Enemy_Stone_Toad = {}
        Props_Enemy_Wall_Walker = {}
        Props_Enemy_Splitter_Command_Module = {}
        Props_Enemy_Splitter_Main_Chassis = {}
        Props_Enemy_Bacteria_Swarm = {}
        Props_Enemy_Minor_Ing = {}
        Props_Enemy_Ing = {}
        Props_Enemy_Ing_Blob_Swarm = {}
        Props_Enemy_Wisp_Tentacle = {}
        Props_Enemy_Medium_Ing = {}
        Props_Enemy_Digital_Guardian = {}
        Props_Enemy_Digital_Guardian_Head = {}
        Props_Enemy_Ing_Space_Jump_Guardian = {}
        Props_Enemy_Ing_Boost_Ball_Guardian = {}
        Props_Enemy_Ing_Spider_ball_Guardian = {}
        Props_Enemy_Sand_Boss = {}
        Props_Enemy_Swamp_Boss_Stage_1 = {}
        Props_Enemy_Swamp_Boss_Stage_2 = {}
        Props_Enemy_Emperor_Ing_Stage_1 = {}
        Props_Enemy_Emperor_Ing_Stage_2_Tentacle = {}
        Props_Enemy_Emperor_Ing_Stage_3 = {}
        Props_Enemy_Puddle_Spore = {}
        Props_Enemy_Dark_Commando = {}
        Props_Enemy_Dark_Trooper = {}
        Props_Enemy_Puffer = {}
        Props_Enemy_Space_Pirate = {}
        Props_Enemy_Commando_Pirate = {}
        Props_Enemy_Flying_Pirate = {}
        Props_Enemy_Metroid_Alpha = {}
        Props_Enemy_Dark_Samus = {}

        #Props_Other_Actor = {} - Currently uneeded
        #Props_Other_Actor_Key_Frame = {} - Currently uneeded
        #Props_Other_AI_Key_Frame = {} - Currently uneeded
        #Props_Other_Actor_Rotate = {} - Currently uneeded
        #Props_Other_Waypoint = {} - Currently uneeded
        #Props_Other_AI_Waypoint = {} - Currently uneeded
        #Props_Other_Ambient_AI = {} - Currently uneeded
        #Props_Other_Area_Attributes = {} - Currently uneeded
        #Props_Other_Area_Damage = {} - Currently uneeded
        Props_Other_Color_Modulate = {}
        Props_Other_Generator = {}
        Props_Other_Safe_Zone = {}
        #Props_Other_Timer = {} - Currently uneeded
        #Props_Other_Sequence_Timer = {} - Currently uneeded
        #Props_Other_World_Light_Fader = {} - Currently uneeded

        #f = open("C:/Users/nevin/AppData/Roaming/Python/Python310/site-packages/open_prime_rando/echoes/enemy_attribute_randomizer/Contraption.txt", "w")
        for world_id in _WORLDS:
            world = editor.get_mlvl(world_id)
            for area in world.areas:
                if area.id in _AREAS_TO_SKIP:
                    continue
                for layer in area.layers:
                    for instance in layer.instances:
                        #if area.name == 'Main Research' and layer.name == 'Contraption':
                            #for x in range(7):
                                #if instance.type == TempTypes[x]:
                                    #print(instance.name, file=f)
                                    #print(instance, file=f)
                        for x in range(59):
                            if instance.type == EnemyTypes[x]:
                                if x == 0:
                                    Props_Enemy_Eye_Ball[instance.id] = instance
                                elif x == 1:
                                    Props_Enemy_Blogg[instance.id] = instance
                                elif x == 2:
                                    Props_Enemy_Flyer_Swarm[instance.id] = instance
                                elif x == 3:
                                    Props_Enemy_Glowbug[instance.id] = instance
                                elif x == 4:
                                    Props_Enemy_Lumite[instance.id] = instance
                                elif x == 5:
                                    Props_Enemy_Mystery_Flyer[instance.id] = instance
                                elif x == 6:
                                    Props_Enemy_Shrieker[instance.id] = instance
                                elif x == 7:
                                    Props_Enemy_Metaree[instance.id] = instance
                                elif x == 8:
                                    Props_Enemy_Shredder[instance.id] = instance
                                elif x == 9:
                                    Props_Enemy_Pillbug[instance.id] = instance
                                elif x == 10:
                                    Props_Enemy_Brizgee[instance.id] = instance
                                elif x == 11:
                                    Props_Enemy_Kralee[instance.id] = instance
                                elif x == 12:
                                    Props_Enemy_Plant_Scarab_Swarm[instance.id] = instance
                                elif x == 13:
                                    Props_Enemy_Krocuss[instance.id] = instance
                                elif x == 14:
                                    Props_Enemy_Crystallite[instance.id] = instance
                                elif x == 15:
                                    Props_Enemy_Sandworm[instance.id] = instance
                                elif x == 16:
                                    Props_Enemy_Grenchler[instance.id] = instance
                                elif x == 17:
                                    Props_Enemy_Sporb_Base[instance.id] = instance
                                elif x == 18:
                                    Props_Enemy_Splinter[instance.id] = instance
                                elif x == 19:
                                    Props_Enemy_Atomic_Alpha[instance.id] = instance
                                elif x == 20:
                                    Props_Enemy_Tryclops[instance.id] = instance
                                elif x == 21:
                                    Props_Enemy_Atomic_Beta[instance.id] = instance
                                elif x == 22:
                                    Props_Enemy_Metaree_Swarm[instance.id] = instance
                                elif x == 23:
                                    Props_Enemy_Rezbit[instance.id] = instance
                                elif x == 24:
                                    Props_Enemy_Octapede_Segment[instance.id] = instance
                                elif x == 25:
                                    Props_Enemy_AI_Manned_Turret[instance.id] = instance
                                elif x == 26:
                                    Props_Enemy_Gun_Turret_Base[instance.id] = instance
                                elif x == 27:
                                    Props_Enemy_Gun_Turret_Top[instance.id] = instance
                                elif x == 28:
                                    Props_Enemy_Elite_Pirate[instance.id] = instance
                                #elif x == 29:
                                    #Props_Enemy_Stone_Toad[instance.id] = instance
                                elif x == 30:
                                    Props_Enemy_Wall_Walker[instance.id] = instance
                                elif x == 31:
                                    Props_Enemy_Splitter_Command_Module[instance.id] = instance
                                elif x == 32:
                                    Props_Enemy_Splitter_Main_Chassis[instance.id] = instance
                                elif x == 33:
                                    Props_Enemy_Bacteria_Swarm[instance.id] = instance
                                elif x == 34:
                                    Props_Enemy_Minor_Ing[instance.id] = instance
                                elif x == 35:
                                    Props_Enemy_Ing[instance.id] = instance
                                elif x == 36:
                                    Props_Enemy_Ing_Blob_Swarm[instance.id] = instance
                                elif x == 37:
                                    Props_Enemy_Wisp_Tentacle[instance.id] = instance
                                elif x == 38:
                                    Props_Enemy_Medium_Ing[instance.id] = instance
                                elif x == 39:
                                    Props_Enemy_Digital_Guardian[instance.id] = instance
                                elif x == 40:
                                    Props_Enemy_Digital_Guardian_Head[instance.id] = instance
                                elif x == 41:
                                    Props_Enemy_Ing_Space_Jump_Guardian[instance.id] = instance
                                elif x == 42:
                                    Props_Enemy_Ing_Boost_Ball_Guardian[instance.id] = instance
                                elif x == 43:
                                    Props_Enemy_Ing_Spider_ball_Guardian[instance.id] = instance
                                elif x == 44:
                                    Props_Enemy_Sand_Boss[instance.id] = instance
                                elif x == 45:
                                    Props_Enemy_Swamp_Boss_Stage_1[instance.id] = instance
                                elif x == 46:
                                    Props_Enemy_Swamp_Boss_Stage_2[instance.id] = instance
                                elif x == 47:
                                    Props_Enemy_Emperor_Ing_Stage_1[instance.id] = instance
                                elif x == 48:
                                    Props_Enemy_Emperor_Ing_Stage_2_Tentacle[instance.id] = instance
                                elif x == 49:
                                    Props_Enemy_Emperor_Ing_Stage_3[instance.id] = instance
                                elif x == 50:
                                    Props_Enemy_Puddle_Spore[instance.id] = instance
                                elif x == 51:
                                    Props_Enemy_Dark_Commando[instance.id] = instance
                                elif x == 52:
                                    Props_Enemy_Dark_Trooper[instance.id] = instance
                                elif x == 53:
                                    Props_Enemy_Puffer[instance.id] = instance
                                elif x == 54:
                                    Props_Enemy_Space_Pirate[instance.id] = instance
                                elif x == 55:
                                    Props_Enemy_Commando_Pirate[instance.id] = instance
                                elif x == 56:
                                    Props_Enemy_Flying_Pirate[instance.id] = instance
                                elif x == 57:
                                    Props_Enemy_Metroid_Alpha[instance.id] = instance
                                elif x == 58:
                                    Props_Enemy_Dark_Samus[instance.id] = instance
                        for x in range(15):
                            if instance.type == OtherTypes[x]:
                                #if x == 0:
                                #    Props_Other_Actor[instance.id] = instance
                                #elif x == 1:
                                #    Props_Other_Actor_Key_Frame[instance.id] = instance
                                #elif x == 2:
                                #    Props_Other_AI_Key_Frame[instance.id] = instance
                                #elif x == 3:
                                #    Props_Other_Actor_Rotate[instance.id] = instance
                                #elif x == 4:
                                #    Props_Other_Waypoint[instance.id] = instance
                                #elif x == 5:
                                #    Props_Other_AI_Waypoint[instance.id] = instance
                                #elif x == 6:
                                #    Props_Other_Ambient_AI[instance.id] = instance
                                #elif x == 7:
                                #    Props_Other_Area_Attributes[instance.id] = instance
                                #elif x == 8:
                                #    Props_Other_Area_Damage[instance.id] = instance
                                if x == 9:
                                    Props_Other_Color_Modulate[instance.id] = instance
                                elif x == 10:
                                    Props_Other_Generator[instance.id] = instance
                                elif x == 11:
                                    Props_Other_Safe_Zone[instance.id] = instance
                                #elif x == 12:
                                #    Props_Other_Timer[instance.id] = instance
                                #elif x == 13:
                                #    Props_Other_Sequence_Timer[instance.id] = instance
                                #elif x == 14:
                                #    Props_Other_World_Light_Fader[instance.id] = instance

        Enemy_Property_List = [Props_Enemy_Eye_Ball, Props_Enemy_Blogg, Props_Enemy_Flyer_Swarm, Props_Enemy_Glowbug, Props_Enemy_Lumite, Props_Enemy_Mystery_Flyer, Props_Enemy_Shrieker, Props_Enemy_Metaree,
                               Props_Enemy_Shredder, Props_Enemy_Pillbug, Props_Enemy_Brizgee, Props_Enemy_Kralee, Props_Enemy_Plant_Scarab_Swarm, Props_Enemy_Krocuss, Props_Enemy_Crystallite, Props_Enemy_Sandworm,
                               Props_Enemy_Grenchler, Props_Enemy_Sporb_Base, Props_Enemy_Splinter, Props_Enemy_Atomic_Alpha, Props_Enemy_Tryclops, Props_Enemy_Atomic_Beta, Props_Enemy_Metaree_Swarm, Props_Enemy_Rezbit,
                               Props_Enemy_Octapede_Segment, Props_Enemy_AI_Manned_Turret, Props_Enemy_Gun_Turret_Base, Props_Enemy_Gun_Turret_Top, Props_Enemy_Elite_Pirate, Props_Enemy_Wall_Walker, Props_Enemy_Splitter_Command_Module,
                               Props_Enemy_Splitter_Main_Chassis, Props_Enemy_Bacteria_Swarm, Props_Enemy_Minor_Ing, Props_Enemy_Ing, Props_Enemy_Ing_Blob_Swarm, Props_Enemy_Wisp_Tentacle, Props_Enemy_Medium_Ing,
                               Props_Enemy_Digital_Guardian, Props_Enemy_Digital_Guardian_Head, Props_Enemy_Ing_Space_Jump_Guardian, Props_Enemy_Ing_Boost_Ball_Guardian, Props_Enemy_Ing_Spider_ball_Guardian,
                               Props_Enemy_Sand_Boss, Props_Enemy_Swamp_Boss_Stage_1, Props_Enemy_Swamp_Boss_Stage_2, Props_Enemy_Emperor_Ing_Stage_1, Props_Enemy_Emperor_Ing_Stage_2_Tentacle, Props_Enemy_Emperor_Ing_Stage_3,
                               Props_Enemy_Puddle_Spore, Props_Enemy_Dark_Commando, Props_Enemy_Dark_Trooper, Props_Enemy_Puffer, Props_Enemy_Space_Pirate, Props_Enemy_Commando_Pirate, Props_Enemy_Flying_Pirate,
                               Props_Enemy_Metroid_Alpha, Props_Enemy_Dark_Samus, Props_Other_Color_Modulate, Props_Other_Generator, Props_Other_Safe_Zone]
        #Enemy_Property_List = "ommited due to discords 2K character limit"
        iteration = -1
        for i in Enemy_Property_List:
            iteration += 1
            for R in i.values():
                globals()[Function_Names[iteration]](R, editor, rng, Range_Dict)

    else:

        for world_id in _WORLDS:
            world = editor.get_mlvl(world_id)
            for area in world.areas:
                if area.id in _AREAS_TO_SKIP:
                    continue
                for layer in area.layers:
                    pass

        #pkl.dump( Enemy_Property_List, open( "C:/Users/nevin/AppData/Roaming/Python/Python310/site-packages/open_prime_rando/echoes/enemy_attribute_randomizer/Vanilla_Instance_Properties.p", "wb" ) )

        Enemy_Property_List = pkl.load( open ("C:/Users/nevin/AppData/Roaming/Python/Python310/site-packages/open_prime_rando/echoes/enemy_attribute_randomizer/Vanilla_Instance_Properties.p", "rb") )

        #print(Enemy_Property_List)

        iteration = -1
        for i in Enemy_Property_List:
            iteration += 1
            for R in i.values():
                #print(R.name)
                globals()[Function_Names[iteration]](R, editor, rng, Range_Dict)
