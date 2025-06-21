import { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { Theme } from '@/types/analysis'

interface InteractiveThemeExplorerProps {
  data: Theme[]
  width?: number
  height?: number
}

export default function InteractiveThemeExplorer({ 
  data, 
  width = 1000, 
  height = 600 
}: InteractiveThemeExplorerProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const [selectedTheme, setSelectedTheme] = useState<Theme | null>(null)

  useEffect(() => {
    if (!data.length || !svgRef.current) return

    // Clear previous chart
    d3.select(svgRef.current).selectAll('*').remove()

    const margin = { top: 40, right: 200, bottom: 60, left: 60 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Scales
    const x = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.count) || 0])
      .range([0, innerWidth])

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.percentage) || 0])
      .range([innerHeight, 0])

    const radius = d3.scaleSqrt()
      .domain([0, d3.max(data, d => d.count) || 0])
      .range([5, 40])

    const color = d3.scaleOrdinal<string>()
      .domain(['positive', 'negative', 'neutral', 'mixed'])
      .range(['#10b981', '#ef4444', '#6b7280', '#f59e0b'])

    const urgencyOpacity = d3.scaleOrdinal<number>()
      .domain(['high', 'medium', 'low'])
      .range([1, 0.7, 0.4])

    // Grid lines
    g.append('g')
      .attr('class', 'grid')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x)
        .tickSize(-innerHeight)
        .tickFormat(() => '')
      )
      .style('stroke-dasharray', '3,3')
      .style('opacity', 0.3)

    g.append('g')
      .attr('class', 'grid')
      .call(d3.axisLeft(y)
        .tickSize(-innerWidth)
        .tickFormat(() => '')
      )
      .style('stroke-dasharray', '3,3')
      .style('opacity', 0.3)

    // Axes
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x))
      .append('text')
      .attr('x', innerWidth / 2)
      .attr('y', 40)
      .attr('fill', '#374151')
      .style('text-anchor', 'middle')
      .text('Number of Mentions')

    g.append('g')
      .call(d3.axisLeft(y))
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', -40)
      .attr('x', -innerHeight / 2)
      .attr('fill', '#374151')
      .style('text-anchor', 'middle')
      .text('Percentage of Responses (%)')

    // Title
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 20)
      .attr('text-anchor', 'middle')
      .style('font-size', '20px')
      .style('font-weight', 'bold')
      .text('Interactive Theme Explorer')

    // Bubbles
    const simulation = d3.forceSimulation<Theme>(data)
      .force('x', d3.forceX<Theme>(d => x(d.count)).strength(1))
      .force('y', d3.forceY<Theme>(d => y(d.percentage)).strength(1))
      .force('collision', d3.forceCollide<Theme>(d => radius(d.count) + 2))
      .stop()

    // Run simulation
    for (let i = 0; i < 120; ++i) simulation.tick()

    // Create bubble groups
    const bubbles = g.selectAll('.bubble')
      .data(data)
      .enter().append('g')
      .attr('class', 'bubble')
      .attr('transform', d => `translate(${(d as any).x || x(d.count)},${(d as any).y || y(d.percentage)})`)
      .style('cursor', 'pointer')

    // Add circles
    bubbles.append('circle')
      .attr('r', 0)
      .attr('fill', d => color(d.sentiment))
      .attr('opacity', d => urgencyOpacity(d.urgency))
      .attr('stroke', d => color(d.sentiment))
      .attr('stroke-width', 2)
      .transition()
      .duration(800)
      .delay((d, i) => i * 50)
      .attr('r', d => radius(d.count))

    // Add labels for large bubbles
    bubbles.filter(d => d.count > 50)
      .append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '.35em')
      .style('font-size', '12px')
      .style('font-weight', '600')
      .style('fill', 'white')
      .style('pointer-events', 'none')
      .text(d => d.name.split(' ').slice(0, 2).join(' '))

    // Interaction
    bubbles
      .on('mouseover', function(event, d) {
        d3.select(this).select('circle')
          .transition()
          .duration(200)
          .attr('r', radius(d.count) * 1.2)
          
        setSelectedTheme(d)
      })
      .on('mouseout', function(event, d) {
        d3.select(this).select('circle')
          .transition()
          .duration(200)
          .attr('r', radius(d.count))
      })

    // Legend
    const legend = svg.append('g')
      .attr('transform', `translate(${width - 180}, 60)`)

    // Sentiment legend
    const sentimentLegend = legend.append('g')
    
    sentimentLegend.append('text')
      .attr('font-weight', 'bold')
      .attr('font-size', '14px')
      .text('Sentiment')

    const sentiments = ['positive', 'negative', 'neutral', 'mixed']
    sentiments.forEach((sentiment, i) => {
      const item = sentimentLegend.append('g')
        .attr('transform', `translate(0, ${20 + i * 20})`)

      item.append('circle')
        .attr('r', 6)
        .attr('fill', color(sentiment))

      item.append('text')
        .attr('x', 15)
        .attr('y', 4)
        .style('font-size', '12px')
        .text(sentiment.charAt(0).toUpperCase() + sentiment.slice(1))
    })

    // Urgency legend
    const urgencyLegend = legend.append('g')
      .attr('transform', 'translate(0, 140)')
    
    urgencyLegend.append('text')
      .attr('font-weight', 'bold')
      .attr('font-size', '14px')
      .text('Urgency')

    const urgencies = ['high', 'medium', 'low']
    urgencies.forEach((urgency, i) => {
      const item = urgencyLegend.append('g')
        .attr('transform', `translate(0, ${20 + i * 20})`)

      item.append('circle')
        .attr('r', 6)
        .attr('fill', '#6b7280')
        .attr('opacity', urgencyOpacity(urgency))

      item.append('text')
        .attr('x', 15)
        .attr('y', 4)
        .style('font-size', '12px')
        .text(urgency.charAt(0).toUpperCase() + urgency.slice(1))
    })

    // Size legend
    const sizeLegend = legend.append('g')
      .attr('transform', 'translate(0, 260)')
    
    sizeLegend.append('text')
      .attr('font-weight', 'bold')
      .attr('font-size', '14px')
      .text('Size = Count')

  }, [data, width, height])

  return (
    <div className="relative">
      <svg ref={svgRef} className="w-full h-full" />
      
      {selectedTheme && (
        <div className="absolute top-4 left-4 bg-white p-4 rounded-lg shadow-lg max-w-sm">
          <h3 className="font-bold text-lg mb-2">{selectedTheme.name}</h3>
          <p className="text-sm text-gray-600 mb-3">{selectedTheme.description}</p>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="font-semibold">Count:</span> {selectedTheme.count}
            </div>
            <div>
              <span className="font-semibold">Percentage:</span> {selectedTheme.percentage.toFixed(1)}%
            </div>
            <div>
              <span className="font-semibold">Sentiment:</span> {selectedTheme.sentiment}
            </div>
            <div>
              <span className="font-semibold">Urgency:</span> {selectedTheme.urgency}
            </div>
          </div>
          {selectedTheme.keywords.length > 0 && (
            <div className="mt-3">
              <span className="font-semibold text-sm">Keywords:</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {selectedTheme.keywords.map((keyword, i) => (
                  <span key={i} className="text-xs bg-gray-100 px-2 py-1 rounded">
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}