# -*- coding: utf-8 -*-
# Copyright 2011, Florent Lamiraux, Thomas Moulard, JRL, CNRS/AIST
#
# This file is part of dynamic-graph.
# dynamic-graph is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# dynamic-graph is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Lesser Public License for more details.  You should have
# received a copy of the GNU Lesser General Public License along with
# dynamic-graph. If not, see <http://www.gnu.org/licenses/>.

from dynamic_graph.sot.core.matrix_util import matrixToTuple, vectorToTuple,rotate, matrixToRPY
from dynamic_graph.sot.core.meta_tasks_kine import *
from numpy import *

from dynamic_graph.sot.romeo.romeo import *
robot = Robot('robot')
plug(robot.device.state, robot.dynamic.position)

from dynamic_graph.ros import *
ros = Ros(robot)


# Create a solver.
from dynamic_graph.sot.dynamics.solver import Solver
solver = Solver(robot)

#-------------------------------------------------------------------------------
#----- MAIN LOOP ---------------------------------------------------------------
#-------------------------------------------------------------------------------
# define the macro allowing to run the simulation.
from dynamic_graph.sot.core.utils.thread_interruptible_loop import loopInThread,loopShortcuts
dt=5e-3
@loopInThread
def inc():
    robot.device.increment(dt)

runner=inc()
[go,stop,next,n]=loopShortcuts(runner)

# ---- TASKS -------------------------------------------------------------------
# ---- TASKS -------------------------------------------------------------------
# ---- TASKS -------------------------------------------------------------------


# ---- TASK GRIP ---
taskRH=MetaTaskKine6d('rh',robot.dynamic,'right-wrist','right-wrist')
handMgrip=eye(4); handMgrip[0:3,3] = (0.1,0,0)
taskRH.opmodif = matrixToTuple(handMgrip)
taskRH.feature.frame('desired')
# robot.tasks['right-wrist'].add(taskRH.feature.name)

# --- STATIC COM (if not walking)
robot.createCenterOfMassFeatureAndTask(
    'featureCom', 'featureComDef', 'comTask',
    selec = '011',
    gain = 10)


# --- CONTACTS
# define contactLF and contactRF
for name,joint in [ ['LF','left-ankle'], ['RF','right-ankle' ] ]:
    contact = MetaTaskKine6d('contact'+name,robot.dynamic,name,joint)
    contact.feature.frame('desired')
    contact.gain.setConstant(10)
    contact.keep()
    locals()['contact'+name] = contact

# --- RUN ----------------------------------------------------------------------

target=(0.5,-0.2,0.8)
gotoNd(taskRH,target,'111',(4.9,0.9,0.01,0.9))

solver.push(contactRF.task)
solver.push(contactLF.task)
solver.push(robot.comTask)
solver.push(taskRH.task)

# type inc to run one iteration, or go to run indefinitely.
# go()
