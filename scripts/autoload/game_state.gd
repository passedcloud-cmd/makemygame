extends Node
## 게임 전체에서 기억해야 하는 값들 (체력, 호감도, 이벤트를 봤는지 등).
## 어느 스크립트에서든 GameState.get_var("affection_b") 처럼 쓸 수 있다.
## 세이브 파일에는 to_dict()로 바꾼 값이 그대로 저장된다.

signal hp_changed(hp: int, max_hp: int)

var max_hp := 5
var hp := 5:
	set(value):
		hp = clampi(value, 0, max_hp)
		hp_changed.emit(hp, max_hp)

var vars: Dictionary = {}
## 플레이 시간 (초). 방 안에서 게임 중일 때만 흐른다 (타이틀, 일시정지 중엔 멈춤).
var playtime := 0.0


func _process(delta: float) -> void:
	if get_tree().current_scene is Room:
		playtime += delta


func get_var(var_name: String) -> int:
	return vars.get(var_name, 0)


func set_var(var_name: String, value: int) -> void:
	vars[var_name] = value


## 새 게임을 시작할 때 모든 값을 처음 상태로 되돌린다.
func reset() -> void:
	max_hp = 5
	hp = max_hp
	vars = {}
	playtime = 0.0


func to_dict() -> Dictionary:
	return {"max_hp": max_hp, "hp": hp, "vars": vars.duplicate(), "playtime": playtime}


func from_dict(data: Dictionary) -> void:
	max_hp = int(data.get("max_hp", 5))
	hp = int(data.get("hp", max_hp))
	playtime = float(data.get("playtime", 0.0))
	vars = {}
	# 세이브 파일(JSON)에서 읽으면 숫자가 소수로 바뀌어 있어서 정수로 되돌린다.
	var saved: Dictionary = data.get("vars", {})
	for key in saved:
		vars[key] = int(saved[key])
