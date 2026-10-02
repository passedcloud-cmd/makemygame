// 회상 장면 효과: 화면을 세피아(빛바랜 사진) 톤으로 바꾸고 가장자리를 어둡게 한다.
shader_type canvas_item;

uniform sampler2D screen_tex : hint_screen_texture, filter_nearest;
// 0 = 효과 없음, 1 = 완전히 회상 톤
uniform float amount : hint_range(0.0, 1.0) = 1.0;

void fragment() {
	vec3 col = texture(screen_tex, SCREEN_UV).rgb;
	float gray = dot(col, vec3(0.299, 0.587, 0.114));
	vec3 sepia = vec3(gray * 1.08 + 0.07, gray * 0.96 + 0.04, gray * 0.78 + 0.01);
	vec2 p = (UV - 0.5) * vec2(16.0 / 9.0, 1.0);
	float edge = smoothstep(1.0, 0.35, length(p));
	sepia *= mix(0.45, 1.0, edge);
	COLOR = vec4(mix(col, sepia, amount), 1.0);
}
