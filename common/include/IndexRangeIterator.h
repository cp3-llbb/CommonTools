#pragma once

#include <boost/iterator/iterator_facade.hpp>

/*
 * Provide an iterator interface over an index that runs from 0 to N
 */
template<typename IDX>
class IndexRangeIterator
  : public boost::iterator_facade<IndexRangeIterator<IDX>,
      IDX, // value
      boost::random_access_traversal_tag,
      IDX  // ref
    >
{
public:
  IndexRangeIterator(IDX idx, IDX max)
    : m_idx{idx}, m_max{max} {}

  IDX dereference() const { return m_idx; }
  bool equal( const IndexRangeIterator& other ) const { return ( m_max == other.m_max ) && ( m_idx == other.m_idx ); }
  void increment() { ++m_idx; }
  void decrement() { --m_idx; }
  void advance(std::ptrdiff_t d) { m_idx += d; }
  std::ptrdiff_t distance_to(const IndexRangeIterator& other) const { return m_idx-other.m_idx; }
private:
  IDX m_idx, m_max;
};
