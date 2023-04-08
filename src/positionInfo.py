def position(): #res : 해상도 tuple // ex : (1280,720) (960, 540)
#    if res==[1280,720]:
    #left, top, dx, dy
    pos = {'aliance':(1015,643,30,30),
            'menu':(1205,643,45,45),
            'wars':(590,375,60,60),
            'loc1':(192,226,100,17),
            'loc2':(192,410,100,17),
            'loc3':(192,594,100,17),
            'castle':(592,328,108,71),
            'info':(735,232,20,20),
            'nickname':(636,249,617,261),
            'info_x':(1078,70,20,20)}
    return pos

def sc_region():
    #left, top, width, height
    sc = {'castle':[-681,93,71,11],
          'bf':[-84,93,71,11]}
    return sc