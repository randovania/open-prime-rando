#The following don't have Patterned:
#FlyingSwarm, PlantScarabSwarm, MetareeSwarm, AIMannedTurret, BacteriaSwarm, IngBlobSwarm

from retro_data_structures.properties.echoes.objects.EyeBall import EyeBall
from retro_data_structures.properties.echoes.objects.Blogg import Blogg
from retro_data_structures.properties.echoes.objects.FlyerSwarm import FlyerSwarm
from retro_data_structures.properties.echoes.objects.Glowbug import Glowbug
from retro_data_structures.properties.echoes.objects.Lumite import Lumite
from retro_data_structures.properties.echoes.objects.MysteryFlyer import MysteryFlyer
from retro_data_structures.properties.echoes.objects.Shrieker import Shrieker
from retro_data_structures.properties.echoes.objects.Metaree import Metaree
from retro_data_structures.properties.echoes.objects.Shredder import Shredder
from retro_data_structures.properties.echoes.objects.PillBug import PillBug
from retro_data_structures.properties.echoes.objects.Brizgee import Brizgee
from retro_data_structures.properties.echoes.objects.Kralee import Kralee
from retro_data_structures.properties.echoes.objects.PlantScarabSwarm import PlantScarabSwarm
from retro_data_structures.properties.echoes.objects.Krocuss import Krocuss
from retro_data_structures.properties.echoes.objects.Crystallite import Crystallite
from retro_data_structures.properties.echoes.objects.Sandworm import Sandworm
from retro_data_structures.properties.echoes.objects.Grenchler import Grenchler
from retro_data_structures.properties.echoes.objects.SporbBase import SporbBase
from retro_data_structures.properties.echoes.objects.Splinter import Splinter
from retro_data_structures.properties.echoes.objects.AtomicAlpha import AtomicAlpha
from retro_data_structures.properties.echoes.objects.Tryclops import Tryclops
from retro_data_structures.properties.echoes.objects.AtomicBeta import AtomicBeta
from retro_data_structures.properties.echoes.objects.MetareeSwarm import MetareeSwarm
from retro_data_structures.properties.echoes.objects.Rezbit import Rezbit
from retro_data_structures.properties.echoes.objects.OctapedeSegment import OctapedeSegment
from retro_data_structures.properties.echoes.objects.AIMannedTurret import AIMannedTurret
from retro_data_structures.properties.echoes.objects.ElitePirate import ElitePirate
from retro_data_structures.properties.echoes.objects.StoneToad import StoneToad
from retro_data_structures.properties.echoes.objects.WallWalker import WallWalker
from retro_data_structures.properties.echoes.objects.SplitterCommandModule import SplitterCommandModule
from retro_data_structures.properties.echoes.objects.SplitterMainChassis import SplitterMainChassis
from retro_data_structures.properties.echoes.objects.BacteriaSwarm import BacteriaSwarm
from retro_data_structures.properties.echoes.objects.MinorIng import MinorIng
from retro_data_structures.properties.echoes.objects.Ing import Ing
from retro_data_structures.properties.echoes.objects.IngBlobSwarm import IngBlobSwarm
from retro_data_structures.properties.echoes.objects.WispTentacle import WispTentacle
from retro_data_structures.properties.echoes.objects.MediumIng import MediumIng
from retro_data_structures.properties.echoes.objects.DigitalGuardian import DigitalGuardian
from retro_data_structures.properties.echoes.objects.DigitalGuardianHead import DigitalGuardianHead
from retro_data_structures.properties.echoes.objects.IngSpaceJumpGuardian import IngSpaceJumpGuardian
from retro_data_structures.properties.echoes.objects.IngBoostBallGuardian import IngBoostBallGuardian
from retro_data_structures.properties.echoes.objects.IngSpiderballGuardian import IngSpiderballGuardian
from retro_data_structures.properties.echoes.objects.SandBoss import SandBoss
from retro_data_structures.properties.echoes.objects.SwampBossStage1 import SwampBossStage1
from retro_data_structures.properties.echoes.objects.SwampBossStage2 import SwampBossStage2
from retro_data_structures.properties.echoes.objects.EmperorIngStage1 import EmperorIngStage1
from retro_data_structures.properties.echoes.objects.EmperorIngStage2Tentacle import EmperorIngStage2Tentacle
from retro_data_structures.properties.echoes.objects.EmperorIngStage3 import EmperorIngStage3
from retro_data_structures.properties.echoes.objects.PuddleSpore import PuddleSpore
from retro_data_structures.properties.echoes.objects.DarkCommando import DarkCommando
from retro_data_structures.properties.echoes.objects.DarkTrooper import DarkTrooper
from retro_data_structures.properties.echoes.objects.Puffer import Puffer
from retro_data_structures.properties.echoes.objects.SpacePirate import SpacePirate
from retro_data_structures.properties.echoes.objects.CommandoPirate import CommandoPirate
from retro_data_structures.properties.echoes.objects.FlyingPirate import FlyingPirate
from retro_data_structures.properties.echoes.objects.MetroidAlpha import MetroidAlpha
from retro_data_structures.properties.echoes.objects.GunTurretBase import GunTurretBase
from retro_data_structures.properties.echoes.objects.GunTurretTop import GunTurretTop
from retro_data_structures.properties.echoes.objects.DarkSamus import DarkSamus

from retro_data_structures.properties.echoes.objects.Actor import Actor
from retro_data_structures.properties.echoes.objects.ActorKeyframe import ActorKeyframe
from retro_data_structures.properties.echoes.objects.AIKeyframe import AIKeyframe
from retro_data_structures.properties.echoes.objects.ActorRotate import ActorRotate
from retro_data_structures.properties.echoes.objects.Waypoint import Waypoint
from retro_data_structures.properties.echoes.objects.AIWaypoint import AIWaypoint
from retro_data_structures.properties.echoes.objects.AmbientAI import AmbientAI
from retro_data_structures.properties.echoes.objects.AreaAttributes import AreaAttributes
from retro_data_structures.properties.echoes.objects.AreaDamage import AreaDamage
#from retro_data_structures.properties.echoes.objects.TimeKeyframe import TimeKeyframe
#from retro_data_structures.properties.echoes.objects.Platform import Platform
# import camera stuff
from retro_data_structures.properties.echoes.objects.ColorModulate import ColorModulate
# import effect
from retro_data_structures.properties.echoes.objects.Generator import Generator
from retro_data_structures.properties.echoes.objects.SafeZone import SafeZone
# import Sound
# import SoundModifier
from retro_data_structures.properties.echoes.objects.Timer import Timer
from retro_data_structures.properties.echoes.objects.SequenceTimer import SequenceTimer
from retro_data_structures.properties.echoes.objects.WorldLightFader import WorldLightFader


EnemyTypes = [EyeBall, Blogg, FlyerSwarm, Glowbug, Lumite, MysteryFlyer, Shrieker, Metaree, Shredder, PillBug, Brizgee, Kralee, PlantScarabSwarm, Krocuss, Crystallite,
              Sandworm, Grenchler, SporbBase, Splinter, AtomicAlpha, Tryclops, AtomicBeta, MetareeSwarm, Rezbit, OctapedeSegment, AIMannedTurret, GunTurretBase, GunTurretTop, ElitePirate,
              StoneToad, WallWalker, SplitterCommandModule, SplitterMainChassis, BacteriaSwarm, MinorIng, Ing, IngBlobSwarm, WispTentacle, MediumIng, DigitalGuardian,
              DigitalGuardianHead, IngSpaceJumpGuardian, IngBoostBallGuardian, IngSpiderballGuardian, SandBoss, SwampBossStage1, SwampBossStage2, EmperorIngStage1,
              EmperorIngStage2Tentacle, EmperorIngStage3, PuddleSpore, DarkCommando, DarkTrooper, Puffer, SpacePirate, CommandoPirate, FlyingPirate, MetroidAlpha, DarkSamus]

OtherTypes = [Actor, ActorKeyframe, AIKeyframe, ActorRotate, Waypoint, AIWaypoint, AmbientAI, AreaAttributes, AreaDamage, ColorModulate, Generator, SafeZone, Timer,
              SequenceTimer, WorldLightFader]
