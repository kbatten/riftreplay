#!/usr/bin/env python

import sys

from rift import combatlog


#cl = combatlog.combatlog(name='log-c4cb2e8b-2e19-4851-a1c4-8e399988050a')
cl = combatlog.combatlog(name='testlog', create=True, overwrite=True)
cl.store(file("/home/ubuntu/data/CombatLog4.txt"))
#cl.store("""21:03:44: ( 3 , T=P#R=C#219831956824878999 , T=N#R=O#9223372037928544350 , T=X#R=X#0 , T=X#R=X#0 , Braks , Darkscale Drake , 105 , 46187323 , Foo Hammer ) Braks's Foo Hammer hits Darkscale Drake for 105 Physical damage.""")

dps = cl.get_dps_by_time("219831956824878999", None, None, 200)

print dps

#cl = combatlog.combatlog(name='testfoo')
#orig=[[11221, 157], [11223, 161], [11224, 138], [11225, 72], [11227, 30], [11228, 139], [11229, 155], [11230, 30], [11231, 210], [11232, 136], [11234, 171], [11237, 168], [11247, 180], [11251, 30], [11252, 39], [11253, 30], [11256, 30], [11257, 169], [11259, 97], [11260, 36], [11262, 139], [11264, 167], [11265, 105], [11268, 28], [11270, 182], [11272, 171], [11273, 130], [11275, 129], [11276, 210], [11277, 33], [11278, 171], [11281, 72], [11282, 135], [11284, 111], [11285, 77], [11288, 30], [11289, 40], [11290, 146], [11292, 154], [11293, 204], [11295, 120], [11296, 171], [11297, 72], [11298, 210], [11300, 132], [11301, 121], [11306, 132], [11308, 140], [11311, 100], [11312, 143], [11314, 128], [11315, 30], [11317, 131], [11319, 136], [11320, 124], [11322, 123], [11338, 205], [11339, 132], [11341, 116], [11344, 132], [11345, 117], [11347, 260], [11348, 103], [11350, 210], [11352, 123], [11353, 127], [11355, 171], [11357, 136], [11359, 30], [11360, 30], [11363, 142], [11364, 30], [11368, 30], [11369, 109], [11370, 210], [11372, 142], [11373, 142], [11378, 119], [11380, 126], [11381, 106], [11386, 125], [11389, 119], [11392, 128], [11400, 105], [11402, 119], [11403, 119], [11405, 131], [11406, 109], [11411, 30], [11412, 30], [11414, 30], [11417, 107], [11420, 126], [11422, 180], [11425, 121], [11427, 127], [11428, 124], [11438, 104], [11441, 126], [11443, 141], [11444, 99], [11450, 171], [11454, 143], [11459, 134], [11460, 188], [11462, 129], [11463, 109], [11466, 121], [11468, 134], [11469, 110], [11474, 185], [11477, 157], [11482, 30], [11486, 121], [11489, 113], [11490, 116], [11499, 127], [11501, 117], [11505, 117], [11507, 108], [11516, 30], [11517, 30], [11523, 213], [11543, 30], [11546, 30], [11548, 30], [11566, 72], [11572, 139], [11574, 30], [11575, 140], [11576, 158], [11580, 128], [11581, 147], [11584, 143], [11585, 42], [11589, 57], [11593, 31], [11594, 129], [11595, 165], [11597, 267], [11598, 134], [11608, 43], [11612, 135], [11614, 135], [11616, 40], [11620, 265], [11622, 134], [11623, 30], [11624, 31], [11626, 30], [11628, 76], [11631, 105], [11632, 138], [11634, 119], [11635, 160], [11639, 36], [11641, 121], [11642, 210], [11643, 47], [11644, 210], [11645, 112], [11647, 128], [11650, 122], [11652, 103], [11653, 133], [11661, 30], [11663, 30], [11664, 210], [11666, 210], [11669, 111], [11670, 30], [11671, 136], [11672, 128]]
#print cl._smooth(orig, 100, 3)
sys.exit()


#cl = combatlog.combatlog(name='testfoo', create=True, overwrite=True)
#cl = combatlog.combatlog(name='testfoo')
#cl.store(file("/home/ubuntu/data/CombatLog3.txt"))
cl.update_index()

#cl.store("""21:03:45: ( 3 , T=P#R=C#219831956824878999 , T=N#R=O#9223372037928544350 , T=X#R=X#0 , T=X#R=X#0 , Braks , Darkscale Drake , 105 , 46187323 , Bar Hammer ) Braks's Bar Hammer hits Darkscale Drake for 105 Physical damage.""")
player_id = cl.get_player_id()
player_name = cl.get_name(player_id)

print player_name + " : " + player_id
print "friends of " + player_name
for friend_id in cl.get_friend_ids(player_id):
    print " " + cl.get_name(friend_id) + " : " + friend_id
print "enemies of " + player_name
for enemy_id in cl.get_enemy_ids(player_id):
    print " " + cl.get_name(enemy_id) + " : " + enemy_id
    
print cl.get_dps(player_id, "9223372038834569843", 100, False)
print cl.get_dps(player_id, "9223372038834569843", 100, True)
#print cl.get_avg_dps(player_id, "9223372038834569843", 100, False)
#print cl.get_avg_dps(player_id, "9223372038834569843", 100, True)
