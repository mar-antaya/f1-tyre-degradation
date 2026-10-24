from streamlit.testing.v1 import AppTest
app=AppTest.from_file('app.py').run(timeout=90)
assert not app.exception, [str(e) for e in app.exception]
assert len(app.get('iframe'))>=1, 'No data replay rendered'
assert len(app.get('plotly_chart'))>=1, 'No interactive chart rendered'
if app.slider:
    slider=app.slider[0]
    value=slider.value
    slider.set_value(value+slider.step if value+slider.step<=slider.max else value-slider.step)
    app.run(timeout=90)
    assert not app.exception, [str(e) for e in app.exception]
print(f'UI passed: {len(app.get("plotly_chart"))} charts, controls respond')
