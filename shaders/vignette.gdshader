// 화면 가장자리를 어둡게 만드는 효과 (비네팅).
// 가운데는 그대로, 바깥으로 갈수록 어두워진다.
shader_type canvas_item;

// 가장자리 어둠의 진하기 (0 = 없음, 1 = 완전 검정)
uniform float strength : hint_range(0.0, 1.0) = 0.6;
// 어두워지기 시작하는 거리 (화면 가운데 기준)
uniform float radius : hint_range(0.0, 1.5) = 0.85;
// 밝은 곳에서 어두운 곳으로 넘어가는 부드러움
uniform float softness : hint_range(0.01, 1.0) = 0.55;
uniform vec4 tint : source_color = vec4(0.03, 0.02, 0.06, 1.0);

void fragment() {
	vec2 p = UV - 0.5;
	p.x *= 16.0 / 9.0;
	float dark = 1.0 - smoothstep(radius, radius - softness, length(p));
	COLOR = vec4(tint.rgb, dark * strength);
}
