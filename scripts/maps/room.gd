class_name Room
extends Node2D
## 맵(방) 하나의 공통 스크립트.
## 카메라가 방 밖(검은 화면)을 비추지 않도록 카메라 범위를 방 크기에 맞춘다.

## 방의 크기 (픽셀). 32의 배수로 맞추면 타일과 딱 맞는다.
@export var room_size := Vector2i(960, 544)
@export var camera: Camera2D
## 방에 들어오자마자 보여줄 대화 (비워두면 없음)
@export_file("*.txt") var intro_dialogue := ""
@export var intro_block := ""


func _ready() -> void:
	if camera:
		camera.limit_left = 0
		camera.limit_top = 0
		camera.limit_right = room_size.x
		camera.limit_bottom = room_size.y
	if not intro_dialogue.is_empty():
		Dialogue.start.call_deferred(intro_dialogue, intro_block)
