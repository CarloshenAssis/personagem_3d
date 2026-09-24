# Armed Mystery - Pacote Completo de Referência Visual & Godot 4.x

Este arquivo ZIP contém todas as folhas de referência visual, planos ortográficos para modelagem no Blender, paleta de cores sólidas e código GDScript pronto para o jogo indie **Armed Mystery**.

## Sumário de Conteúdo:
1. `/referencias_visuais/`:
   - `01_folha_principal_turnaround_3_vistas.jpg`: Frontal, Lateral e Traseira alinhadas em Pose A neutra.
   - `02_closeup_rosto_e_materiais.jpg`: Detalhe poligonal da face e acabamento fosco dos materiais.
   - `03_vista_frontal_ortografica_1to1.jpg`: Vista isolada frontal para o plano de fundo do Blender.
   - `04_vista_lateral_perfil_ortografica.jpg`: Vista isolada de perfil para espessura e curvatura da coluna.
   - `05_contexto_em_jogo_mansao.jpg`: Cena multiplayer atmosférica na mansão com múltiplos jogadores idênticos.

2. `/godot_scripts/`:
   - `MysteryPlayer.gd`: Controlador CharacterBody3D com altura de 1.80m, câmera FPS e sistema de papéis neutros.
   - `mat_mystery_neutral.tres`: Recurso StandardMaterial3D pré-configurado para Godot 4.x.
   - `proporcoes_anatomicas_180m.json`: Tabela de 8 cabeças e alturas de juntas anatômicas.

3. `/materiais_paleta/`:
   - `paleta_cores_solidas.json`: Dados em Hex, RGB e formato Color() da Godot Engine.
   - `especificacoes_pbr.txt`: Roughness, Metallic e diretrizes anti-reflexo para iluminação em penumbra.

## Regra de Ouro do Game Design (Armed Mystery):
O mesmo modelo 3D é utilizado para **Assassino**, **Detetive** e **Vítimas**. Nenhuma arma fixa na cintura, máscara ou distintivo aparece na malha externa do personagem, garantindo que o mistério dependa unicamente de atitudes e dedução social dos jogadores!
