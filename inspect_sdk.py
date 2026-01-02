import vertexai.preview.reasoning_engines as re
try:
    from vertexai.preview.reasoning_engines import templates
    print("Available in templates:", dir(templates))
except ImportError:
    print("Could not import templates.")

print("Available in reasoning_engines:", dir(re))
