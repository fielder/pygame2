import ctypes

import pygame

c_drawer = None
do_quit = 0

fps_framecount = 0
fps_last_start = 0
fps_rate = 0.0

draw_buf = ""
scanline_buffers = []

surf = None
surf_w = 0
surf_h = 0
surf_p = 0


def refreshScreen():
    global fps_framecount
    global fps_last_start
    global fps_rate

    # draw
    c_drawer.drawPalette(draw_buf, surf_w, surf_h, surf_p)

    # copy the draw buffer to the SDL surface
    if surf_p == surf_w:
        surf.get_buffer().write(draw_buf, 0)
    else:
        prox = surf.get_buffer()
        dest = 0
        for scanline in scanline_buffers:
            prox.write(scanline, dest)
            dest += surf_p

    # update screen
    pygame.display.flip()

    # calc framerate
    fps_framecount += 1
    now = pygame.time.get_ticks()
    if (now - fps_last_start) > 250:
        fps_rate = fps_framecount / ((now - fps_last_start) / 1000.0)
        fps_last_start = now
        fps_framecount = 0


# setup
c_drawer = ctypes.cdll.LoadLibrary("./c_drawer.so")

pygame.init()
pygame.display.set_mode((320, 240), pygame.DOUBLEBUF, 8)

surf = pygame.display.get_surface()
surf_w = surf.get_width()
surf_h = surf.get_height()
surf_p = surf.get_pitch()

draw_buf = ctypes.create_string_buffer("\x00" * (surf_w * surf_h), surf_w * surf_h)

# We're using Pygame's buffer proxy mechanism to write pixels directly
# to the surface. The proxy write() method takes a string and offset.
# In the easy case, we just write the whole buffer at offset 0. However,
# SDL can give us a surface with non-contiguous scanlines. In this case,
# we'll need to write out a scanline at a time. We use python's built-in
# buffer object to make pulling scanlines out of the draw buffer pretty
# snappy. The buffer object allows us to get sub-strings (scanlines) out
# of the main draw buffer without having to slice out copies of each
# scanline every frame.
if surf_p != surf_w:
    for y in xrange(surf_h):
        scanline_buffers.append(buffer(draw_buf, y * surf_w, surf_w))

# loop
while not do_quit:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            do_quit = 1
        elif ev.type == pygame.KEYUP:
            if ev.key == pygame.K_ESCAPE:
                do_quit = 1
            elif ev.key == ord("f"):
                print fps_rate

    refreshScreen()

# shutdown
pygame.quit()
