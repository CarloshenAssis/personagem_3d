extends CharacterBody3D
class_name MysteryPlayer

# ==============================================================================
# ARMED MYSTERY - Core Player Controller (Godot 4.x)
# O mesmo modelo visual é instanciado para todas as funções:
# VITIMA, DETETIVE e ASSASSINO. Nenhuma pista visual é revelada!
# ==============================================================================

enum PlayerRole {
	VICTIM,      # Vítima: Deve sobreviver e completar tarefas
	DETECTIVE,   # Detetive: Possui scanner e revólver secreto guardado
	KILLER       # Assassino: Possui arma letal que só pode ser sacada em segredo
}

@export var role: PlayerRole = PlayerRole.VICTIM
@export var character_height: float = 1.80
@export var walk_speed: float = 3.6
@export var sprint_speed: float = 6.2
@export var mouse_sensitivity: float = 0.0025

# Referências a nós internos
@onready var head: Node3D = $Head
@onready var camera: Camera3D = $Head/Camera3D
@onready var mesh_instance: Node3D = $VisualMesh
@onready var animation_player: AnimationPlayer = $VisualMesh/AnimationPlayer
@onready var collision_shape: CollisionShape3D = $CollisionShape3D

var gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity")

func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	_setup_collision()
	# Se for o cliente local, oculta a cabeça para não obstruir visão em 1ª pessoa
	if is_multiplayer_authority():
		_setup_first_person_shadow_mesh()

func _setup_collision() -> void:
	var capsule = collision_shape.shape as CapsuleShape3D
	if capsule:
		capsule.height = character_height # 1.80m
		capsule.radius = 0.35              # 0.70m de envergadura total
	collision_shape.position.y = character_height / 2.0

func _setup_first_person_shadow_mesh() -> void:
	# No Godot 4, podemos definir 'cast_shadow = SHADOW_CASTING_SETTING_SHADOWS_ONLY'
	# para a cabeça/tronco no jogador local, evitando clipping com a câmera
	pass

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y -= gravity * delta

	var input_dir := Input.get_vector("move_left", "move_right", "move_forward", "move_backward")
	var direction := (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
	var current_speed = sprint_speed if Input.is_action_pressed("sprint") else walk_speed

	if direction:
		velocity.x = direction.x * current_speed
		velocity.z = direction.z * current_speed
		_update_animations("walk" if current_speed == walk_speed else "run")
	else:
		velocity.x = move_toward(velocity.x, 0, current_speed)
		velocity.z = move_toward(velocity.z, 0, current_speed)
		_update_animations("idle")

	move_and_slide()

func _update_animations(anim_name: String) -> void:
	if animation_player and animation_player.has_animation(anim_name):
		if animation_player.current_animation != anim_name:
			animation_player.play(anim_name)
