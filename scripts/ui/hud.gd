extends CanvasLayer
## 화면 왼쪽 위의 체력 하트.

const HEART_SHEET := preload("res://art/ui/hearts.png")

@onready var _hearts: HBoxContainer = $Hearts


func _ready() -> void:
	GameState.hp_changed.connect(_refresh)
	_refresh(GameState.hp, GameState.max_hp)


func _refresh(hp: int, max_hp: int) -> void:
	for child in _hearts.get_children():
		child.queue_free()
	for i in max_hp:
		var heart := TextureRect.new()
		var atlas := AtlasTexture.new()
		atlas.atlas = HEART_SHEET
		atlas.region = Rect2(0 if i < hp else 9, 0, 9, 8)
		heart.texture = atlas
		_hearts.add_child(heart)
