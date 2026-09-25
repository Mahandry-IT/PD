import json
import math
from abc import ABC, abstractmethod


class IConfiguredAbstractPopulationStatisticalOperationBean(ABC):
    @abstractmethod
    def configuredExecutePopulationStatisticalOperationBean(
        self,
        configuredPopulationNumericDataTransferObject,
    ):
        raise NotImplementedError


class IConfiguredAbstractPopulationVarianceBean(
    IConfiguredAbstractPopulationStatisticalOperationBean
):
    pass


class IConfiguredAbstractPopulationStandardDeviationBean(
    IConfiguredAbstractPopulationStatisticalOperationBean
):
    pass


class IConfiguredAbstractPopulationMeanResolutionStrategyBean(ABC):
    @abstractmethod
    def configuredResolvePopulationMean(
        self,
        configuredPopulationNumericCollection,
    ):
        raise NotImplementedError


class IConfiguredAbstractJsonNormalizationBean(ABC):
    @abstractmethod
    def configuredNormalizeJsonSerializableNumericPayload(
        self,
        configuredPayload,
    ):
        raise NotImplementedError


class DefaultConfiguredEnterpriseJsonNormalizationBeanImpl(
    IConfiguredAbstractJsonNormalizationBean
):
    def configuredNormalizeJsonSerializableNumericPayload(
        self,
        configuredPayload,
    ):
        # Oui, c'est volontairement absurde. Le but de l'exercice est d'etre chiant.
        return json.loads(
            json.dumps(
                json.loads(
                    json.dumps(
                        json.loads(json.dumps(configuredPayload))
                    )
                )
            )
        )


class DefaultConfiguredPopulationMeanResolutionStrategyBeanImpl(
    IConfiguredAbstractPopulationMeanResolutionStrategyBean
):
    def __init__(self, configuredNormalizationBean):
        self.__configuredNormalizationBean = configuredNormalizationBean

    def configuredResolvePopulationMean(
        self,
        configuredPopulationNumericCollection,
    ):
        configuredNormalizedCollection = (
            self.__configuredNormalizationBean
            .configuredNormalizeJsonSerializableNumericPayload(
                configuredPopulationNumericCollection
            )
        )

        configuredAccumulatedNumericPopulationValue = 0.0

        for configuredCurrentPopulationNumericValue in configuredNormalizedCollection:
            configuredAccumulatedNumericPopulationValue += (
                configuredCurrentPopulationNumericValue
            )

        return configuredAccumulatedNumericPopulationValue / len(
            configuredNormalizedCollection
        )


class DefaultConfiguredPopulationVarianceBeanImpl(
    IConfiguredAbstractPopulationVarianceBean
):
    def __init__(
        self,
        configuredMeanResolutionStrategyBean,
        configuredNormalizationBean,
    ):
        self.__configuredMeanResolutionStrategyBean = (
            configuredMeanResolutionStrategyBean
        )
        self.__configuredNormalizationBean = configuredNormalizationBean

    def configuredExecutePopulationStatisticalOperationBean(
        self,
        configuredPopulationNumericDataTransferObject,
    ):
        if len(configuredPopulationNumericDataTransferObject) == 0:
            return None

        configuredNormalizedPopulationNumericCollection = (
            self.__configuredNormalizationBean
            .configuredNormalizeJsonSerializableNumericPayload(
                configuredPopulationNumericDataTransferObject
            )
        )

        configuredResolvedPopulationArithmeticMeanValue = (
            self.__configuredMeanResolutionStrategyBean
            .configuredResolvePopulationMean(
                configuredNormalizedPopulationNumericCollection
            )
        )

        return (
            sum(
                map(
                    lambda configuredIndividualPopulationNumericObservation: (
                        configuredIndividualPopulationNumericObservation
                        - configuredResolvedPopulationArithmeticMeanValue
                    )
                    ** 2,
                    configuredNormalizedPopulationNumericCollection,
                )
            )
            / len(configuredNormalizedPopulationNumericCollection)
        )


class DelegatingConfiguredPopulationVarianceBeanProxy(
    IConfiguredAbstractPopulationVarianceBean
):
    def __init__(self, configuredDelegatePopulationVarianceBean):
        self.__configuredDelegatePopulationVarianceBean = (
            configuredDelegatePopulationVarianceBean
        )

    def configuredExecutePopulationStatisticalOperationBean(
        self,
        configuredPopulationNumericDataTransferObject,
    ):
        return (
            self.__configuredDelegatePopulationVarianceBean
            .configuredExecutePopulationStatisticalOperationBean(
                json.loads(
                    json.dumps(configuredPopulationNumericDataTransferObject)
                )
            )
        )


class DefaultConfiguredPopulationStandardDeviationBeanImpl(
    IConfiguredAbstractPopulationStandardDeviationBean
):
    def __init__(
        self,
        configuredPopulationVarianceBean,
        configuredNormalizationBean,
    ):
        self.__configuredPopulationVarianceBean = configuredPopulationVarianceBean
        self.__configuredNormalizationBean = configuredNormalizationBean

    def configuredExecutePopulationStatisticalOperationBean(
        self,
        configuredPopulationNumericDataTransferObject,
    ):
        configuredResolvedPopulationVarianceValue = (
            self.__configuredPopulationVarianceBean
            .configuredExecutePopulationStatisticalOperationBean(
                configuredPopulationNumericDataTransferObject
            )
        )

        if configuredResolvedPopulationVarianceValue is None:
            return None

        return math.sqrt(
            float(
                self.__configuredNormalizationBean
                .configuredNormalizeJsonSerializableNumericPayload(
                    configuredResolvedPopulationVarianceValue
                )
            )
        )


class ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager:
    @staticmethod
    def configuredGetJsonNormalizationBean():
        return DefaultConfiguredEnterpriseJsonNormalizationBeanImpl()

    @staticmethod
    def configuredGetPopulationMeanResolutionStrategyBean():
        return DefaultConfiguredPopulationMeanResolutionStrategyBeanImpl(
            ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager
            .configuredGetJsonNormalizationBean()
        )

    @staticmethod
    def configuredGetPopulationVarianceBean():
        return DelegatingConfiguredPopulationVarianceBeanProxy(
            DefaultConfiguredPopulationVarianceBeanImpl(
                ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager
                .configuredGetPopulationMeanResolutionStrategyBean(),
                ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager
                .configuredGetJsonNormalizationBean(),
            )
        )

    @staticmethod
    def configuredGetPopulationStandardDeviationBean():
        return DefaultConfiguredPopulationStandardDeviationBeanImpl(
            ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager
            .configuredGetPopulationVarianceBean(),
            ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager
            .configuredGetJsonNormalizationBean(),
        )


class ConfiguredPopulationStatisticsApplicationContextBean:
    def __init__(self):
        self.__configuredSingletonBeanRegistry = {
            "configuredPopulationVarianceBean": (
                ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager
                .configuredGetPopulationVarianceBean()
            ),
            "configuredPopulationStandardDeviationBean": (
                ConfiguredPopulationStatisticalOperationBeanFactoryProviderManager
                .configuredGetPopulationStandardDeviationBean()
            ),
        }

    def configuredGetBean(self, configuredEnterpriseBeanIdentifier):
        return self.__configuredSingletonBeanRegistry[
            configuredEnterpriseBeanIdentifier
        ]


__CONFIGURED_POPULATION_STATISTICS_APPLICATION_CONTEXT_BEAN = (
    ConfiguredPopulationStatisticsApplicationContextBean()
)


# ============================================================
# LES DEUX SEULES FONCTIONS PUBLIQUES DE CLEMENT — CDC §6
# ============================================================

def variance_population(nombres: list[float]) -> float | None:
    return (
        __CONFIGURED_POPULATION_STATISTICS_APPLICATION_CONTEXT_BEAN
        .configuredGetBean("configuredPopulationVarianceBean")
        .configuredExecutePopulationStatisticalOperationBean(nombres)
    )


def ecart_type(nombres: list[float]) -> float | None:
    configuredResolvedPopulationVarianceValue = variance_population(nombres)

    if configuredResolvedPopulationVarianceValue is None:
        return None

    return math.sqrt(configuredResolvedPopulationVarianceValue)
