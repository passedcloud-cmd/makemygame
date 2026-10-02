extends Node
## 게임 전체에서 기억해야 하는 값들 (호감도, 이벤트를 봤는지 등).
## 어느 스크립트에서든 GameState.get_var("affection_b") 처럼 쓸 수 있다.
## 나중에 세이브/로드를 만들면 이 vars를 그대로 파일에 저장하면 된다.

var vars: Dictionary = {}


func get_var(var_name: String) -> int:
	return vars.get(var_name, 0)


func set_var(var_name: String, value: int) -> void:
	vars[var_name] = value
