extends Node
## 게임 전체에서 기억해야 하는 값들 (체력, 호감도, 이벤트를 봤는지 등).
## 어느 스크립트에서든 GameState.get_var("affection_b") 처럼 쓸 수 있다.
## 나중에 세이브/로드를 만들면 이 값들을 그대로 파일에 저장하면 된다.

signal hp_changed(hp: int, max_hp: int)

var max_hp := 5
var hp := 5:
	set(value):
		hp = clampi(value, 0, max_hp)
		hp_changed.emit(hp, max_hp)

var vars: Dictionary = {}


func get_var(var_name: String) -> int:
	return vars.get(var_name, 0)


func set_var(var_name: String, value: int) -> void:
	vars[var_name] = value
