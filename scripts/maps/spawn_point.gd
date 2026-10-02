class_name SpawnPoint
extends Marker2D
## 다른 방에서 넘어왔을 때 주인공이 서는 자리.
## 노드 이름이 곧 지점 이름이다 (문의 Target Spawn에 이 이름을 적는다).

## 도착했을 때 바라볼 방향
@export var facing: CharacterSprite.Facing = CharacterSprite.Facing.DOWN
