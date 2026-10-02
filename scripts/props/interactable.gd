class_name Interactable
extends Area2D
## 주인공이 이 영역을 바라보고 Z(확인)를 누르면 대화가 시작된다.
## 상자, 그림, 문 같은 "조사할 수 있는 것"에 붙여서 쓴다.

## 충돌 레이어 3번 ("interact"). 주인공의 조사 영역이 이 레이어만 감지한다.
const LAYER := 1 << 2

## 읽을 대본 파일
@export_file("*.txt") var dialogue_file := ""
## 대본 안에서 시작할 블록 이름 (== 뒤에 쓴 이름)
@export var block := ""


func _ready() -> void:
	collision_layer = LAYER
	collision_mask = 0
	monitoring = false


func interact() -> void:
	Dialogue.start(dialogue_file, block)
