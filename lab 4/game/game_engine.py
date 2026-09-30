import pygame
from .marble import Marble
from .wall import Wall

# Game Engine

WHITE = (255, 255, 255)
DARK = (40, 40, 50)
WALL_COLOR = (90, 90, 110)
GOAL_COLOR = (60, 200, 120)
LOSE_COLOR = (230, 80, 80)
HINT_COLOR = (190, 190, 205)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.tilt_strength = 0.6
        self.friction = 0.02
        self.max_speed = 9

        self.walls = self._build_maze()
        self.goal_x, self.goal_y, self.goal_radius = width - 60, height - 60, 22

        self.time_limit_ms = 45000

        self.font = pygame.font.SysFont("Arial", 26)
        self.title_font = pygame.font.SysFont("Arial", 52, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 20)

        self.quit_requested = False
        self.reset()

    def reset(self):
        self.marble = Marble(50, 50)
        self.start_ticks = pygame.time.get_ticks()
        self.game_over = False
        self.result = None  # "solved" or "timeout"
        self.finish_time_ms = None
        self.end_elapsed_ms = None  # timer value frozen at game over

    def _build_maze(self):
        walls = []
        t = 16  # wall thickness

        # outer boundary
        walls.append(Wall(0, 0, self.width, t))
        walls.append(Wall(0, self.height - t, self.width, t))
        walls.append(Wall(0, 0, t, self.height))
        walls.append(Wall(self.width - t, 0, t, self.height))

        # a few internal walls forming a simple winding path
        walls.append(Wall(0, 140, self.width - 140, t))
        walls.append(Wall(140, 260, self.width - 140, t))
        walls.append(Wall(0, 380, self.width - 140, t))

        return walls

    def handle_event(self, event):
        # Tilting is driven by the continuous mouse position (see
        # handle_input); key presses are only used on the end screen.
        if not self.game_over or event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
            self.reset()
        elif event.key in (pygame.K_ESCAPE, pygame.K_q):
            self.quit_requested = True

    def handle_input(self):
        if self.game_over:
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - self.width // 2
        dy = mouse_y - self.height // 2
        dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        ax = (dx / dist) * self.tilt_strength
        ay = (dy / dist) * self.tilt_strength
        self.marble.vx += ax
        self.marble.vy += ay

    def update(self):
        if self.game_over:
            return

        elapsed = pygame.time.get_ticks() - self.start_ticks
        if elapsed >= self.time_limit_ms:
            self.game_over = True
            self.result = "timeout"
            self.end_elapsed_ms = self.time_limit_ms
            return

        self.marble.vx *= (1 - self.friction)
        self.marble.vy *= (1 - self.friction)

        speed = (self.marble.vx ** 2 + self.marble.vy ** 2) ** 0.5
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.marble.vx *= scale
            self.marble.vy *= scale

        self.marble.x += self.marble.vx
        self.marble.y += self.marble.vy

        self._resolve_wall_collisions()

        gx = self.goal_x - self.marble.x
        gy = self.goal_y - self.marble.y
        if (gx ** 2 + gy ** 2) ** 0.5 <= self.goal_radius:
            self.game_over = True
            self.result = "solved"
            self.finish_time_ms = elapsed
            self.end_elapsed_ms = elapsed

    def _resolve_wall_collisions(self):
        bounce = 0.3
        r = self.marble.radius

        for wall in self.walls:
            wall_rect = wall.rect()

            # True circle-vs-rectangle test: find the point on the wall
            # closest to the marble's centre and only collide if that
            # point lies within the marble's radius. This stops the
            # "phantom" bounces near corners that the old square
            # bounding-box check caused.
            closest_x = max(wall_rect.left, min(self.marble.x, wall_rect.right))
            closest_y = max(wall_rect.top, min(self.marble.y, wall_rect.bottom))
            dx = self.marble.x - closest_x
            dy = self.marble.y - closest_y
            dist_sq = dx * dx + dy * dy

            if dist_sq >= r * r:
                continue

            if dist_sq > 0:
                # Centre is outside the wall: push out along the line
                # from the closest point to the centre (this also gives
                # a natural diagonal bounce off corners).
                dist = dist_sq ** 0.5
                nx, ny = dx / dist, dy / dist
                penetration = r - dist
            else:
                # Centre is inside the wall (very fast move): push out
                # through whichever side is nearest.
                pushes = [
                    (self.marble.x - wall_rect.left, -1, 0),
                    (wall_rect.right - self.marble.x, 1, 0),
                    (self.marble.y - wall_rect.top, 0, -1),
                    (wall_rect.bottom - self.marble.y, 0, 1),
                ]
                depth, nx, ny = min(pushes)
                penetration = depth + r

            self.marble.x += nx * penetration
            self.marble.y += ny * penetration

            # Reflect only the part of the velocity heading into the wall.
            v_normal = self.marble.vx * nx + self.marble.vy * ny
            if v_normal < 0:
                self.marble.vx -= (1 + bounce) * v_normal * nx
                self.marble.vy -= (1 + bounce) * v_normal * ny

    def render(self, screen):
        screen.fill(DARK)

        for wall in self.walls:
            pygame.draw.rect(screen, WALL_COLOR, wall.rect())

        pygame.draw.circle(screen, GOAL_COLOR, (self.goal_x, self.goal_y), self.goal_radius)
        pygame.draw.circle(screen, WHITE, (int(self.marble.x), int(self.marble.y)), self.marble.radius)

        if self.game_over:
            elapsed = self.end_elapsed_ms  # freeze the timer at game over
        else:
            elapsed = pygame.time.get_ticks() - self.start_ticks
        seconds_left = max(0, (self.time_limit_ms - elapsed) // 1000)
        timer_text = self.font.render(f"Time: {seconds_left}s", True, WHITE)
        screen.blit(timer_text, (10, 10))

        if self.game_over:
            self._render_end_screen(screen)

    def _render_end_screen(self, screen):
        # Dim the maze behind a translucent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        if self.result == "solved":
            title, color = "Maze Solved!", GOAL_COLOR
            detail = f"Finished in {self.finish_time_ms / 1000:.1f}s"
        else:
            title, color = "Time's Up!", LOSE_COLOR
            detail = "The maze was not solved"

        cx, cy = self.width // 2, self.height // 2
        panel = pygame.Rect(0, 0, 440, 200)
        panel.center = (cx, cy + 5)
        pygame.draw.rect(screen, DARK, panel, border_radius=14)
        pygame.draw.rect(screen, color, panel, width=3, border_radius=14)

        lines = [
            (self.title_font.render(title, True, color), cy - 50),
            (self.font.render(detail, True, WHITE), cy + 10),
            (self.small_font.render("Press R to play again  |  Esc to quit", True, HINT_COLOR), cy + 60),
        ]
        for surface, y in lines:
            screen.blit(surface, surface.get_rect(center=(cx, y)))
