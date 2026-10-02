class_name Characters
extends RefCounted
## 대화에 나오는 캐릭터 정보 (화면에 보일 이름, 이름표 색).
## 이름이 정해지면 "name"만 바꾸면 된다. 대본에서는 계속 A, B, C로 써도 OK.

const DATA := {
	"A": {"name": "A", "color": Color("f5d03f")},
	"B": {"name": "B", "color": Color("8ccbec")},
	"C": {"name": "C", "color": Color("a5b85c")},
}

## 얼굴 그림 폴더. "A.png"가 기본 얼굴, "A_smile.png"처럼 _표정을 붙이면 표정별 얼굴.
const PORTRAIT_DIR := "res://art/portraits/"
## 스탠딩 일러 폴더. 파일 이름 규칙은 얼굴 그림과 같다.
const STANDING_DIR := "res://art/standing/"


static func display_name(id: String) -> String:
	return DATA[id].name if DATA.has(id) else id


static func color(id: String) -> Color:
	return DATA[id].color if DATA.has(id) else Color("d8d0e0")


## 표정 그림이 있으면 그걸, 없으면 기본 얼굴을, 그것도 없으면 null을 돌려준다.
static func portrait(id: String, expression: String) -> Texture2D:
	return _find(PORTRAIT_DIR, id, expression)


## 스탠딩 일러. 찾는 규칙은 portrait()와 같다.
static func standing(id: String, expression: String) -> Texture2D:
	return _find(STANDING_DIR, id, expression)


static func _find(dir: String, id: String, expression: String) -> Texture2D:
	var paths: Array[String] = []
	if not expression.is_empty():
		paths.append(dir + "%s_%s.png" % [id, expression])
	paths.append(dir + "%s.png" % id)
	for path in paths:
		if ResourceLoader.exists(path):
			return load(path)
	return null
