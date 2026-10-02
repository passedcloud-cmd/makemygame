class_name Monster
extends CharacterBody2D
## 기본 몬스터. 평소엔 어슬렁거리다가 주인공이 가까이 오면 쫓아온다.
## 주인공에게 닿으면 피해를 주고, 공격을 맞으면 밀려나며 체력이 줄어든다.

@export var max_hp := 3
## 어슬렁거릴 때 속도
@export var wander_speed := 20.0
## 쫓아올 때 속도 (주인공은 90)
@export var chase_speed := 45.0
## 이 거리 안에 주인공이 들어오면 쫓아온다
@export var detect_range := 120.0
## 닿았을 때 주인공에게 주는 피해
@export var contact_damage := 1

var hp := 0
var _knockback := Vector2.ZERO
var _stun := 0.0
var _wander_dir := Vector2.ZERO
var _wander_timer := 0.0
var _anim_time := 0.0
var _dead := false

@onready var sprite: Sprite2D = $Sprite
@onready var contact_area: Area2D = $ContactArea


func _ready() -> void:
	hp = max_hp


func _physics_process(delta: float) -> void:
	if _dead:
		return
	_anim_time += delta
	sprite.frame = int(_anim_time * 3.0) % 2
	if Dialogue.active or Transition.busy:
		return

	var player := _find_player()
	var move := Vector2.ZERO
	_stun = maxf(_stun - delta, 0.0)
	if _stun <= 0.0:
		if player and global_position.distance_to(player.global_position) < detect_range:
			move = global_position.direction_to(player.global_position) * chase_speed
		else:
			move = _wander(delta)

	velocity = move + _knockback
	_knockback = _knockback.move_toward(Vector2.ZERO, 700.0 * delta)
	move_and_slide()

	for body in contact_area.get_overlapping_bodies():
		if body is Player:
			body.take_damage(contact_damage, global_position)


func _wander(delta: float) -> Vector2:
	_wander_timer -= delta
	if _wander_timer <= 0.0:
		_wander_timer = randf_range(1.0, 2.5)
		# 절반은 멈춰 있고, 절반은 아무 방향으로나 걷는다
		_wander_dir = Vector2.ZERO if randf() < 0.5 else Vector2.from_angle(randf() * TAU)
	return _wander_dir * wander_speed


func _find_player() -> Player:
	return get_tree().get_first_node_in_group("player") as Player


## 주인공의 공격에 맞았을 때 불린다.
func take_hit(damage: int, from: Vector2) -> void:
	if _dead:
		return
	hp -= damage
	_knockback = (global_position - from).normalized() * 160.0
	_stun = 0.3
	# 맞으면 붉게 번쩍
	sprite.modulate = Color(2.5, 1.0, 1.2)
	create_tween().tween_property(sprite, "modulate", Color.WHITE, 0.2)
	if hp <= 0:
		_die()


func _die() -> void:
	_dead = true
	collision_layer = 0
	contact_area.monitoring = false
	var tween := create_tween().set_parallel()
	tween.tween_property(sprite, "scale", Vector2(1.6, 0.2), 0.25)
	tween.tween_property(sprite, "modulate:a", 0.0, 0.25)
	tween.chain().tween_callback(queue_free)
