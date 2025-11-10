# 🎨 Role Gallery / Sample Outputs
st.markdown("### 🎨 Role Gallery / Sample Outputs")
st.info(f"Sample outputs for **{role}**:")

sample_outputs = {
    "🎬 Film Director": """
- Suggests using close-up shots for emotional impact.
- Recommends dynamic camera angles for action sequences.
- Emphasizes color grading to enhance mood.
- Advises pacing adjustments to maintain tension.
""",
    "💃 Dance Coach": """
- Focus on core stability and fluid arm movements.
- Suggests practicing counts with music to improve timing.
- Recommends stretching routines for flexibility.
- Gives tips for expressive facial gestures.
""",
    "👗 Fashion Stylist": """
- Pair pastel colors with neutral accessories.
- Suggests layering textures for depth in outfits.
- Advises choosing clothing to complement body shapes.
- Recommends seasonal wardrobe color palettes.
""",
    "🎨 Art Critic": """
- Notice the contrast between light and shadow in the composition.
- Analyze symbolism and hidden meanings in the work.
- Comment on balance and visual harmony of elements.
- Suggest improvements in color choices or perspective.
""",
    "🎹 Music Composer": """
- Try a minor chord progression to enhance tension.
- Suggests adding counter-melodies for richness.
- Emphasizes dynamics to create emotional impact.
- Recommends tempo changes for dramatic effect.
""",
    "📝 Creative Writer": """
- Suggests using vivid imagery to immerse the reader.
- Provides ideas for character development.
- Offers plot twists to heighten suspense.
- Gives feedback on narrative pacing and dialogue.
""",
    "📸 Photographer": """
- Advises shooting during golden hour for natural light.
- Suggests framing subjects with leading lines.
- Recommends experimenting with depth of field.
- Emphasizes capturing emotion and storytelling.
""",
    "🎭 Theatre Actor": """
- Recommends projecting voice to reach the audience.
- Suggests practicing gestures for authenticity.
- Advises on timing and pauses for dramatic effect.
- Focus on emotional connection with scene partners.
""",
    "🎥 Film Editor": """
- Suggests cutting scenes for better pacing.
- Recommends transitions that match the tone.
- Advises layering sound and visuals for impact.
- Emphasizes rhythm and continuity in sequences.
""",
    "🎤 Performance Coach": """
- Guides on voice modulation for clarity and emotion.
- Recommends body posture exercises to boost confidence.
- Provides tips for managing stage anxiety.
- Suggests engaging the audience through interaction.
"""
}

st.write(sample_outputs.get(role, "Sample outputs not available."))
