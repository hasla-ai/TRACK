
현재 Transform 중심 구조
1. 
Player Transform
       │
       └── Camera Transform
Camera가 Player의 자식이면 (Camera의 parent=player_transform)
Player
 └── Camera가 되고,
Player가 Yaw를 담당하고 Camera가 Pitch를 담당.

즉. Camera의 월드 회전은 자동으로: Player Yaw + Camera Pitch.

Player Yaw: Player Y rotation -> Camera World rotation Y
Camera Pitch: Camera Local X rotation -> Camera World rotation X

따라서 Camera World Rotation = Player Yaw + Camera Pitch.

2. 
Player Transform
├── position
│   └── X/Y/Z = 실제 이동 상태
│
└── rotation
    └── Y = 실제 Yaw 상태
3. 
Camera Transform
└── rotation
    └── X = 실제 Pitch 상태


그리고 렌더링:

Camera Transform
   ├── World Position
   └── World Rotation
          ↓
   world_to_camera()


상태변수 제거
player_x
player_y
player_z
player_yaw
player_pitch
camera_x
camera_y
camera_z
camera_yaw


Camera 위치도:

Player World Position
        +
Camera Local Position (0, 2, 0)
        ↓
Camera World Position




Transform.rotation
        │
        │ degree
        ↓
   계산 직전 radians 변환
        │
        ↓
sin / cos