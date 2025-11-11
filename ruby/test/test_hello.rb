require 'minitest/autorun'
require_relative '../lib/hello'

class TestHello < Minitest::Test
  def setup
    @hello = HelloWasm::Hello.new
  end
  
  def test_greet
    result = @hello.greet('World')
    assert_equal 'Hello, World!', result
  end
  
  def test_add
    result = @hello.add(5, 3)
    assert_equal 8, result
  end
end
