import { Copy, Users, Store, Car, Layers } from 'lucide-react'
import type { LayerDefinition, LayerType } from './types'

export const layerRegistry: Record<LayerType, LayerDefinition> = {
  deep_clone: {
    type: 'deep_clone',
    label: 'Deep Clone',
    description: 'Clone a successful business model to this location',
    icon: Copy,
    color: 'emerald',
    aiKeywords: ['clone', 'copy', 'replicate', 'business model', 'franchise', 'similar'],
    inputs: [
      {
        key: 'sourceBusiness',
        label: 'Source Business',
        type: 'text',
        placeholder: 'Search for a business to clone...',
        required: true
      },
      {
        key: 'businessType',
        label: 'Business Category',
        type: 'select',
        options: [
          { value: 'restaurant', label: 'Restaurant' },
          { value: 'retail', label: 'Retail Store' },
          { value: 'service', label: 'Service Business' },
          { value: 'fitness', label: 'Fitness/Gym' },
          { value: 'healthcare', label: 'Healthcare' },
          { value: 'other', label: 'Other' }
        ],
        defaultValue: 'restaurant'
      },
      {
        key: 'analyzeCompetitors',
        label: 'Include Competitor Analysis',
        type: 'toggle',
        defaultValue: true
      }
    ],
    defaultConfig: {
      sourceBusiness: '',
      businessType: 'restaurant',
      analyzeCompetitors: true
    }
  },

  demographics: {
    type: 'demographics',
    label: 'Demographics',
    description: 'Population, income, and age distribution data',
    icon: Users,
    color: 'blue',
    aiKeywords: ['demographics', 'population', 'income', 'age', 'census', 'people'],
    inputs: [
      {
        key: 'showPopulation',
        label: 'Population Density',
        type: 'toggle',
        defaultValue: true
      },
      {
        key: 'showIncome',
        label: 'Median Income',
        type: 'toggle',
        defaultValue: true
      },
      {
        key: 'showAge',
        label: 'Age Distribution',
        type: 'toggle',
        defaultValue: false
      },
      {
        key: 'displayMode',
        label: 'Display Mode',
        type: 'select',
        options: [
          { value: 'heatmap', label: 'Heatmap' },
          { value: 'markers', label: 'Data Points' },
          { value: 'choropleth', label: 'Choropleth' }
        ],
        defaultValue: 'heatmap'
      }
    ],
    defaultConfig: {
      showPopulation: true,
      showIncome: true,
      showAge: false,
      displayMode: 'heatmap'
    }
  },

  competition: {
    type: 'competition',
    label: 'Competition',
    description: 'Find competitors and similar businesses nearby',
    icon: Store,
    color: 'orange',
    aiKeywords: ['competition', 'competitors', 'nearby', 'similar', 'businesses', 'stores'],
    inputs: [
      {
        key: 'searchQuery',
        label: 'Business Type',
        type: 'text',
        placeholder: 'e.g., coffee shops, gyms, restaurants...',
        required: true
      },
      {
        key: 'showRatings',
        label: 'Show Ratings',
        type: 'toggle',
        defaultValue: true
      },
      {
        key: 'showReviews',
        label: 'Show Review Count',
        type: 'toggle',
        defaultValue: true
      },
      {
        key: 'minRating',
        label: 'Minimum Rating',
        type: 'select',
        options: [
          { value: '0', label: 'Any' },
          { value: '3', label: '3+ Stars' },
          { value: '4', label: '4+ Stars' },
          { value: '4.5', label: '4.5+ Stars' }
        ],
        defaultValue: '0'
      }
    ],
    defaultConfig: {
      searchQuery: '',
      showRatings: true,
      showReviews: true,
      minRating: '0'
    }
  },

  traffic: {
    type: 'traffic',
    label: 'Traffic',
    description: 'Foot traffic and transportation patterns',
    icon: Car,
    color: 'amber',
    aiKeywords: ['traffic', 'footfall', 'transportation', 'busy', 'transit'],
    inputs: [
      {
        key: 'showFootTraffic',
        label: 'Foot Traffic',
        type: 'toggle',
        defaultValue: true
      },
      {
        key: 'showTransit',
        label: 'Public Transit',
        type: 'toggle',
        defaultValue: false
      },
      {
        key: 'timeOfDay',
        label: 'Time of Day',
        type: 'select',
        options: [
          { value: 'all', label: 'All Day' },
          { value: 'morning', label: 'Morning (6am-12pm)' },
          { value: 'afternoon', label: 'Afternoon (12pm-6pm)' },
          { value: 'evening', label: 'Evening (6pm-12am)' }
        ],
        defaultValue: 'all'
      }
    ],
    defaultConfig: {
      showFootTraffic: true,
      showTransit: false,
      timeOfDay: 'all'
    }
  },

  custom: {
    type: 'custom',
    label: 'Custom Layer',
    description: 'Create a custom data layer',
    icon: Layers,
    color: 'gray',
    aiKeywords: ['custom', 'create', 'new', 'layer'],
    inputs: [
      {
        key: 'name',
        label: 'Layer Name',
        type: 'text',
        placeholder: 'Enter layer name...',
        required: true
      },
      {
        key: 'dataSource',
        label: 'Data Source',
        type: 'select',
        options: [
          { value: 'manual', label: 'Manual Entry' },
          { value: 'csv', label: 'CSV Upload' },
          { value: 'api', label: 'API Endpoint' }
        ],
        defaultValue: 'manual'
      }
    ],
    defaultConfig: {
      name: '',
      dataSource: 'manual'
    }
  }
}

export const defaultLayerTabs: LayerType[] = ['deep_clone', 'demographics', 'competition', 'traffic']

export function getLayerDefinition(type: LayerType): LayerDefinition {
  return layerRegistry[type]
}

export function createLayerInstance(type: LayerType, id?: string): import('./types').LayerInstance {
  const definition = layerRegistry[type]
  return {
    id: id || `${type}_${Date.now()}`,
    type,
    config: { ...definition.defaultConfig },
    visible: true,
    loading: false,
    data: null,
    error: null
  }
}
