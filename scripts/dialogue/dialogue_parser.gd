class_name DialogueParser
extends RefCounted
## 대화 대본(.txt)을 읽어서 게임이 실행할 수 있는 명령 목록으로 바꾼다.
## 대본 쓰는 법은 dialogue/README.md 참고.
##
## 결과는 { "블록 이름": [명령, 명령, ...] } 모양의 Dictionary.
## 명령 하나는 {"type": "say", "speaker": "A", ...} 같은 Dictionary.

const SET_OPS: Array[String] = ["=", "+", "-"]
const COMPARE_OPS: Array[String] = [">=", "<=", ">", "<", "==", "!="]

## "이름(표정): 대사" 모양을 찾는 패턴
static var _say_re := RegEx.create_from_string("^([^\\s:()]+)\\s*(?:\\(([^)]*)\\))?\\s*:\\s*(.+)$")


static func parse_file(path: String) -> Dictionary:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		push_error("대본 파일을 열 수 없음: %s" % path)
		return {}
	return parse(file.get_as_text(), path)


static func parse(text: String, source := "") -> Dictionary:
	var blocks := {}
	var current: Array = []
	var block_name := ""
	var line_no := 0
	for raw in text.split("\n"):
		line_no += 1
		var line := raw.strip_edges()
		if line.is_empty() or line.begins_with("#"):
			continue
		if line.begins_with("=="):
			block_name = line.substr(2).strip_edges()
			current = []
			blocks[block_name] = current
			continue
		if block_name.is_empty():
			push_error("%s:%d 블록(== 이름) 밖에 쓴 줄은 무시됨" % [source, line_no])
			continue
		var cmd := _parse_line(line)
		if cmd.is_empty():
			push_error("%s:%d 문법을 이해할 수 없음: %s" % [source, line_no, line])
			continue
		# 연달아 쓴 선택지(*)들은 하나의 선택지 묶음으로 합친다.
		if cmd.type == "choice":
			if current.is_empty() or current.back().type != "choices":
				current.append({"type": "choices", "options": []})
			current.back().options.append(cmd.option)
		else:
			current.append(cmd)
	return blocks


static func _parse_line(line: String) -> Dictionary:
	# * 선택지 -> 블록
	if line.begins_with("*"):
		var parts := line.substr(1).split("->")
		if parts.size() != 2:
			return {}
		return {"type": "choice", "option": {
			"text": parts[0].strip_edges(), "target": parts[1].strip_edges()}}

	# -> 블록
	if line.begins_with("->"):
		return {"type": "jump", "target": line.substr(2).strip_edges()}

	if line == "end":
		return {"type": "end"}

	# set 변수 + 1
	if line.begins_with("set "):
		var p := line.substr(4).split(" ", false)
		if p.size() != 3 or not p[1] in SET_OPS:
			return {}
		return {"type": "set", "name": p[0], "op": p[1], "value": p[2].to_int()}

	# if 변수 >= 2 -> 블록
	if line.begins_with("if "):
		var halves := line.substr(3).split("->")
		if halves.size() != 2:
			return {}
		var p := halves[0].strip_edges().split(" ", false)
		if p.size() != 3 or not p[1] in COMPARE_OPS:
			return {}
		return {"type": "if", "name": p[0], "op": p[1], "value": p[2].to_int(),
			"target": halves[1].strip_edges()}

	# 이름(표정): 대사
	var m := _say_re.search(line)
	if m:
		return {"type": "say", "speaker": m.get_string(1),
			"expression": m.get_string(2).strip_edges(), "text": m.get_string(3)}

	# 그 외는 전부 나레이션
	return {"type": "say", "speaker": "", "expression": "", "text": line}
