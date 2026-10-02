class_name Door
extends Area2D
## 주인공이 걸어 들어오면 다른 방으로 이동하는 문.

## 이동할 방 장면
@export_file("*.tscn") var target_scene := ""
## 그 방의 어느 지점(SpawnPoint 이름)에 도착할지
@export var target_spawn := ""


func _ready() -> void:
	collision_layer = 0
	collision_mask = 1
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node2D) -> void:
	if body is Player and not Transition.busy and not Dialogue.active:
		Transition.change_room(target_scene, target_spawn)
