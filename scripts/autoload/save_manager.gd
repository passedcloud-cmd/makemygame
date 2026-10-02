extends Node
## 세이브/로드. 어디서든 SaveManager.save_game(1), SaveManager.load_game(1)처럼 쓴다.
##
## 세이브 파일은 user:// 폴더에 save_1.json ~ save_3.json으로 저장된다.
## (윈도우: %APPDATA%/Godot/app_userdata/MakeMyGame/)
## JSON이라 메모장으로 열어서 내용을 확인할 수 있다.

const SLOT_COUNT := 3
## 세이브 파일 형식이 바뀌면 숫자를 올린다 (옛날 세이브 호환 처리용)
const VERSION := 1


func slot_path(slot: int) -> String:
	return "user://save_%d.json" % slot


## 지금 상태를 슬롯에 저장한다. 방 안에서만 저장할 수 있다.
func save_game(slot: int) -> bool:
	var room := get_tree().current_scene as Room
	var player := get_tree().get_first_node_in_group("player") as Player
	if room == null or player == null:
		return false
	var data := {
		"version": VERSION,
		"saved_at": Time.get_datetime_string_from_system(false, true),
		"room_scene": room.scene_file_path,
		"room_name": room.room_name,
		"player_x": player.global_position.x,
		"player_y": player.global_position.y,
		"facing": int(player.sprite.facing),
		"state": GameState.to_dict(),
	}
	var file := FileAccess.open(slot_path(slot), FileAccess.WRITE)
	if file == null:
		push_error("세이브 파일을 쓸 수 없음: %s" % slot_path(slot))
		return false
	file.store_string(JSON.stringify(data, "\t"))
	return true


## 슬롯의 세이브 내용을 읽는다. 비어 있거나 망가졌으면 빈 Dictionary.
func read_slot(slot: int) -> Dictionary:
	if not FileAccess.file_exists(slot_path(slot)):
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(slot_path(slot)))
	if not parsed is Dictionary or not parsed.has("room_scene"):
		return {}
	return parsed


func has_any_save() -> bool:
	for slot in range(1, SLOT_COUNT + 1):
		if not read_slot(slot).is_empty():
			return true
	return false


## 슬롯을 불러와서 저장했던 방, 저장했던 자리로 이동한다.
func load_game(slot: int) -> bool:
	var data := read_slot(slot)
	if data.is_empty():
		return false
	GameState.from_dict(data.get("state", {}))
	get_tree().paused = false
	Transition.change_room_at(data.room_scene,
		Vector2(data.get("player_x", 0.0), data.get("player_y", 0.0)),
		int(data.get("facing", 0)))
	return true


## 슬롯 목록에 보여줄 한 줄 설명
func describe(slot: int) -> String:
	var data := read_slot(slot)
	if data.is_empty():
		return "슬롯 %d   - 비어 있음 -" % slot
	var seconds := int(data.get("state", {}).get("playtime", 0.0))
	var time := "%02d:%02d:%02d" % [seconds / 3600, seconds / 60 % 60, seconds % 60]
	var saved_at: String = data.get("saved_at", "").substr(0, 16)
	return "슬롯 %d   %s   %s   %s" % [slot, data.get("room_name", "?"), time, saved_at]
